import json
import re
from datetime import datetime
from metadata_provider import extract_metadata

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return {"$date": obj.isoformat() + "Z"}
        return super().default(obj)

class DynamicQueryGenerator:
    def __init__(self):
        self.metadata = extract_metadata()
        self.collections = list(self.metadata.keys())
        
    def analyze_question(self, question):
        """Analyze user question to determine intent and relevant collections"""
        question_lower = question.lower()
        
        # Find mentioned collections or related terms
        relevant_collections = []
        
        # Product queries should analyze orders with product joins
        if any(word in question_lower for word in ['product', 'products', 'item', 'items']):
            if 'orders' in self.collections:
                relevant_collections.append('orders')
        
        # Sales/revenue queries should target orders collection
        elif any(word in question_lower for word in ['sales', 'revenue', 'total sales', 'income']):
            if 'orders' in self.collections:
                relevant_collections.append('orders')
        
        # Customer queries should target customers collection
        elif any(word in question_lower for word in ['customer', 'customers', 'client', 'clients']):
            if 'customers' in self.collections:
                relevant_collections.append('customers')
        
        # Direct collection mentions
        for collection in self.collections:
            if collection.lower() in question_lower:
                relevant_collections.append(collection)
        
        # If no direct collection match, look for field names
        if not relevant_collections:
            for collection, info in self.metadata.items():
                fields = info.get('fields', {})
                for field in fields.keys():
                    if field.lower() in question_lower:
                        relevant_collections.append(collection)
                        break
        
        # For sales/revenue/product queries, default to orders
        if not relevant_collections:
            if any(word in question_lower for word in ['sales', 'revenue', 'total', 'amount', 'product', 'sold', 'least', 'most']):
                relevant_collections = ['orders']
            else:
                relevant_collections = [self.collections[0]] if self.collections else ['orders']
            
        return {
            'collections': relevant_collections,
            'intent': self._determine_intent(question_lower),
            'filters': self._extract_filters(question)
        }
    
    def _determine_intent(self, question):
        """Determine what the user wants to do"""
        if any(word in question for word in ['least', 'worst', 'lowest', 'bottom']):
            return 'min_analysis'
        elif any(word in question for word in ['most', 'best', 'highest', 'top']):
            return 'max_analysis'
        elif any(word in question for word in ['total sales', 'total revenue', 'sales total']):
            return 'aggregate_sum'
        elif any(word in question for word in ['total', 'sum', 'sales', 'revenue']):
            return 'aggregate_sum'
        elif any(word in question for word in ['count', 'how many', 'number of']):
            return 'count'
        elif any(word in question for word in ['average', 'avg', 'mean']):
            return 'average'
        elif any(word in question for word in ['show', 'list', 'display', 'get']):
            return 'list'
        elif any(word in question for word in ['max', 'maximum', 'highest']):
            return 'max'
        elif any(word in question for word in ['min', 'minimum', 'lowest']):
            return 'min'
        else:
            return 'list'
    
    def _extract_filters(self, question):
        """Extract date ranges, status filters, etc."""
        filters = {}
        
        # Extract year
        year_match = re.search(r'20\d{2}', question)
        if year_match:
            year = year_match.group()
            filters['year'] = year
            
        # Extract status mentions
        if 'completed' in question.lower():
            filters['status'] = 'completed'
        elif 'pending' in question.lower():
            filters['status'] = 'pending'
        elif 'cancelled' in question.lower():
            filters['status'] = 'cancelled'
            
        return filters
    
    def generate_query(self, question):
        """Generate MongoDB query based on question analysis"""
        analysis = self.analyze_question(question)
        collection = analysis['collections'][0]
        intent = analysis['intent']
        filters = analysis['filters']
        
        # Build match stage
        match_stage = {}
        
        # Add date filter if year specified
        if 'year' in filters:
            year = int(filters['year'])
            date_fields = self._find_date_fields(collection)
            if date_fields:
                date_field = date_fields[0]
                from datetime import datetime
                match_stage[date_field] = {
                    "$gte": datetime(year, 1, 1),
                    "$lt": datetime(year + 1, 1, 1)
                }
        
        # Add status filter if specified or if it's a sales query
        if 'status' in filters and self._has_field(collection, 'status'):
            match_stage['status'] = filters['status']
        elif intent == 'aggregate_sum' and self._has_field(collection, 'status'):
            # For sales queries, default to completed orders
            match_stage['status'] = 'completed'
        
        # Build pipeline based on intent
        pipeline = []
        
        if match_stage:
            pipeline.append({"$match": match_stage})
        
        if intent == 'count':
            pipeline.append({"$count": "total"})
            
        elif intent == 'aggregate_sum':
            amount_field = self._find_amount_field(collection)
            if amount_field:
                pipeline.append({
                    "$group": {
                        "_id": None,
                        "total": {"$sum": f"${amount_field}"}
                    }
                })
            else:
                pipeline.append({"$count": "total"})
                
        elif intent == 'average':
            amount_field = self._find_amount_field(collection)
            if amount_field:
                pipeline.append({
                    "$group": {
                        "_id": None,
                        "average": {"$avg": f"${amount_field}"}
                    }
                })
                
        elif intent == 'min_analysis':
            # For product analysis queries like "which product sold least"
            if any(word in question.lower() for word in ['product', 'item']):
                pipeline.extend([
                    {
                        "$group": {
                            "_id": "$productId",
                            "totalSales": {"$sum": "$amount"},
                            "quantitySold": {"$sum": "$quantity"}
                        }
                    },
                    {
                        "$lookup": {
                            "from": "products",
                            "localField": "_id",
                            "foreignField": "_id",
                            "as": "product"
                        }
                    },
                    {"$unwind": "$product"},
                    {
                        "$project": {
                            "productName": "$product.name",
                            "totalSales": 1,
                            "quantitySold": 1
                        }
                    },
                    {"$sort": {"totalSales": 1}},  # Ascending for least
                    {"$limit": 10}
                ])
            else:
                amount_field = self._find_amount_field(collection)
                if amount_field:
                    pipeline.append({
                        "$group": {
                            "_id": None,
                            "min": {"$min": f"${amount_field}"}
                        }
                    })
                    
        elif intent == 'max_analysis':
            # For product analysis queries like "which product sold most"
            if any(word in question.lower() for word in ['product', 'item']):
                pipeline.extend([
                    {
                        "$group": {
                            "_id": "$productId",
                            "totalSales": {"$sum": "$amount"},
                            "quantitySold": {"$sum": "$quantity"}
                        }
                    },
                    {
                        "$lookup": {
                            "from": "products",
                            "localField": "_id",
                            "foreignField": "_id",
                            "as": "product"
                        }
                    },
                    {"$unwind": "$product"},
                    {
                        "$project": {
                            "productName": "$product.name",
                            "totalSales": 1,
                            "quantitySold": 1
                        }
                    },
                    {"$sort": {"totalSales": -1}},  # Descending for most
                    {"$limit": 10}
                ])
            else:
                amount_field = self._find_amount_field(collection)
                if amount_field:
                    pipeline.append({
                        "$group": {
                            "_id": None,
                            "max": {"$max": f"${amount_field}"}
                        }
                    })
                
        else:  # list intent
            pipeline.extend([
                {"$sort": {self._find_date_fields(collection)[0]: -1}} if self._find_date_fields(collection) else {"$sort": {"_id": -1}},
                {"$limit": 10}
            ])
        
        return json.dumps(pipeline, cls=DateTimeEncoder), collection
    
    def _find_amount_field(self, collection):
        """Find fields that likely contain monetary amounts"""
        if collection not in self.metadata:
            return None
            
        fields = self.metadata[collection].get('fields', {})
        amount_candidates = ['amount', 'total', 'price', 'cost', 'value', 'revenue', 'sales']
        
        for candidate in amount_candidates:
            for field_name in fields.keys():
                if candidate in field_name.lower():
                    return field_name
        return None
    
    def _find_date_fields(self, collection):
        """Find fields that contain dates"""
        if collection not in self.metadata:
            return []
            
        fields = self.metadata[collection].get('fields', {})
        date_fields = []
        
        for field_name, field_type in fields.items():
            if field_type == 'date' or 'date' in field_name.lower() or 'time' in field_name.lower():
                date_fields.append(field_name)
                
        return date_fields
    
    def _has_field(self, collection, field_name):
        """Check if collection has a specific field"""
        if collection not in self.metadata:
            return False
        return field_name in self.metadata[collection].get('fields', {})

# Global instance
query_generator = DynamicQueryGenerator()

def generate_mongo_query(prompt: str) -> str:
    """Dynamic query generation that adapts to any database schema"""
    try:
        query, collection = query_generator.generate_query(prompt)
        return query
    except Exception as e:
        # Fallback to simple query
        return json.dumps([{"$limit": 10}], cls=DateTimeEncoder)