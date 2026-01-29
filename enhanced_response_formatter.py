#!/usr/bin/env python3
"""
Enhanced Response Formatter - Better business context formatting
"""

class EnhancedResponseFormatter:
    def __init__(self):
        pass
    
    def format_enhanced_response(self, question, raw_data):
        """Format response with enhanced business intelligence"""
        question_lower = question.lower()
        
        if isinstance(raw_data, str) and "Error" in raw_data:
            return f"❌ **Error:** {raw_data}\n\n💡 Try: 'total sales', 'top customers', or 'recent orders'"
        
        if not isinstance(raw_data, list) or len(raw_data) == 0:
            return self._format_no_data_response(question)
        
        # Detect response type
        first_item = raw_data[0]
        
        # Churn analysis
        if 'customerName' in str(first_item) and 'lastOrderDate' in str(first_item):
            return self._format_churn_analysis(raw_data)
        
        # Seasonal analysis
        if 'monthName' in str(first_item) and 'totalSales' in str(first_item):
            return self._format_seasonal_analysis(raw_data)
        
        # Product performance
        if 'productName' in str(first_item) and 'totalSales' in str(first_item):
            return self._format_product_performance(raw_data, question)
        
        # Customer performance
        if 'customerName' in str(first_item) and 'totalSpent' in str(first_item):
            return self._format_customer_performance(raw_data, question)
        
        # City analysis
        if 'city' in str(first_item) and 'totalSales' in str(first_item):
            return self._format_city_analysis(raw_data)
        
        # Sales summary
        if isinstance(first_item, dict) and len(first_item) <= 3 and 'totalSales' in str(first_item):
            return self._format_sales_summary(raw_data, question)
        
        # Count results
        if isinstance(first_item, dict) and 'total' in first_item and len(first_item) == 1:
            return self._format_count_result(raw_data, question)
        
        # Aggregation results
        if isinstance(first_item, dict) and '_id' in first_item and len(first_item) == 2:
            return self._format_aggregation_result(raw_data, question)
        
        # Generic list
        return self._format_generic_list(raw_data, question)
    
    def _format_churn_analysis(self, data):
        """Format churn analysis results"""
        response = f"🚨 **Customer Churn Analysis**\n\n"
        response += f"Found **{len(data)}** customers who haven't ordered recently:\n\n"
        
        for i, customer in enumerate(data[:10], 1):
            name = customer.get('customerName', 'Unknown')
            last_order = customer.get('lastOrderDate', 'Unknown')
            total_spent = customer.get('totalSpent', 0)
            orders = customer.get('totalOrders', 0)
            
            # Calculate days since last order
            if isinstance(last_order, str):
                days_ago = "90+ days"
            else:
                from datetime import datetime
                days = (datetime.now() - last_order).days
                days_ago = f"{days} days"
            
            response += f"{i}. **{name}** - Last order: {days_ago} ago\n"
            response += f"   💰 Total spent: ${total_spent:,.2f} ({orders} orders)\n\n"
        
        response += "💡 **Recommendation:** Consider reaching out with personalized offers to re-engage these customers."
        return response
    
    def _format_seasonal_analysis(self, data):
        """Format seasonal analysis results"""
        response = "📅 **Seasonal Sales Analysis**\n\n"
        
        total_sales = sum(item.get('totalSales', 0) for item in data)
        
        for item in data:
            month = item.get('monthName', 'Unknown')
            sales = item.get('totalSales', 0)
            orders = item.get('orderCount', 0)
            
            percentage = (sales / total_sales * 100) if total_sales > 0 else 0
            
            response += f"📊 **{month}:** ${sales:,.2f} ({percentage:.1f}% of total, {orders:,} orders)\n"
        
        # Find best and worst months
        if len(data) > 1:
            best_month = max(data, key=lambda x: x.get('totalSales', 0))
            worst_month = min(data, key=lambda x: x.get('totalSales', 0))
            
            response += f"\n🏆 **Best month:** {best_month.get('monthName')} (${best_month.get('totalSales', 0):,.2f})\n"
            response += f"📉 **Slowest month:** {worst_month.get('monthName')} (${worst_month.get('totalSales', 0):,.2f})"
        
        return response
    
    def _format_product_performance(self, data, question):
        """Format product performance results"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['worst', 'least', 'bottom', 'lowest']):
            response = "📉 **Worst Performing Products**\n\n"
        else:
            response = "📈 **Top Performing Products**\n\n"
        
        for i, item in enumerate(data[:10], 1):
            name = item.get('productName', 'Unknown')
            sales = item.get('totalSales', 0)
            quantity = item.get('quantitySold', 0)
            orders = item.get('orderCount', 0)
            
            response += f"{i}. **{name}**\n"
            response += f"   💰 Sales: ${sales:,.2f} | 📦 Units: {quantity:,} | 🛒 Orders: {orders:,}\n\n"
        
        return response
    
    def _format_customer_performance(self, data, question):
        """Format customer performance results"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['worst', 'least', 'bottom', 'lowest']):
            response = "📉 **Lowest Value Customers**\n\n"
        else:
            response = "👑 **Top Value Customers**\n\n"
        
        for i, item in enumerate(data[:10], 1):
            name = item.get('customerName', 'Unknown')
            spent = item.get('totalSpent', 0)
            orders = item.get('orderCount', 0)
            avg_order = item.get('avgOrderValue', 0)
            city = item.get('customerCity', 'Unknown')
            
            response += f"{i}. **{name}** ({city})\n"
            response += f"   💰 Spent: ${spent:,.2f} | 🛒 Orders: {orders} | 📊 Avg: ${avg_order:.2f}\n\n"
        
        return response
    
    def _format_city_analysis(self, data):
        """Format city analysis results"""
        response = "🗺️ **Sales by Location**\n\n"
        
        total_sales = sum(item.get('totalSales', 0) for item in data)
        
        for i, item in enumerate(data, 1):
            city = item.get('city', item.get('_id', 'Unknown'))
            sales = item.get('totalSales', 0)
            orders = item.get('orderCount', 0)
            customers = item.get('customerCount', 0)
            
            percentage = (sales / total_sales * 100) if total_sales > 0 else 0
            
            response += f"{i}. **{city}** - ${sales:,.2f} ({percentage:.1f}%)\n"
            response += f"   🛒 {orders:,} orders"
            if customers > 0:
                response += f" | 👥 {customers:,} customers"
            response += "\n\n"
        
        return response
    
    def _format_sales_summary(self, data, question):
        """Format sales summary"""
        question_lower = question.lower()
        first_item = data[0]
        
        total_sales = first_item.get('totalSales', first_item.get('total', 0))
        order_count = first_item.get('orderCount', 0)
        
        # Determine time context
        time_context = ""
        if 'this year' in question_lower or '2024' in question_lower:
            time_context = " for 2024"
        elif 'last year' in question_lower or '2023' in question_lower:
            time_context = " for 2023"
        
        response = f"💰 **Sales Summary{time_context}**\n\n"
        response += f"**Total Revenue:** ${total_sales:,.2f}\n"
        
        if order_count > 0:
            avg_order_value = total_sales / order_count
            response += f"**Total Orders:** {order_count:,}\n"
            response += f"**Average Order Value:** ${avg_order_value:.2f}\n"
        
        # Add business insights
        if total_sales > 1000000:
            response += f"\n🎉 Excellent performance! Revenue exceeded $1M{time_context}."
        elif total_sales > 500000:
            response += f"\n👍 Good performance! Strong revenue{time_context}."
        
        return response
    
    def _format_count_result(self, data, question):
        """Format count results"""
        question_lower = question.lower()
        count = data[0].get('total', 0)
        
        if 'customer' in question_lower:
            return f"👥 **Customer Count:** {count:,} customers in the database"
        elif 'product' in question_lower:
            return f"📦 **Product Count:** {count:,} products in the catalog"
        elif 'order' in question_lower:
            return f"🛒 **Order Count:** {count:,} orders in the system"
        else:
            return f"📊 **Total Count:** {count:,} records found"
    
    def _format_aggregation_result(self, data, question):
        """Format aggregation results"""
        question_lower = question.lower()
        first_item = data[0]
        
        for key, value in first_item.items():
            if key != '_id' and isinstance(value, (int, float)):
                if any(word in question_lower for word in ['sales', 'revenue']):
                    return f"💰 **Total Sales:** ${value:,.2f}"
                elif 'average' in question_lower:
                    return f"📊 **Average Value:** ${value:.2f}"
                else:
                    return f"📊 **Result:** {value:,.2f}"
        
        return f"📊 **Result:** {first_item}"
    
    def _format_generic_list(self, data, question):
        """Format generic list results"""
        response = "📋 **Results:**\n\n"
        
        for i, item in enumerate(data[:10], 1):
            if isinstance(item, dict):
                if 'name' in item:
                    response += f"{i}. **{item['name']}**"
                    if 'email' in item:
                        response += f" - {item['email']}"
                    if 'city' in item:
                        response += f" ({item['city']})"
                    if 'price' in item:
                        response += f" - ${item['price']}"
                    response += "\n"
                else:
                    fields = [f"{k}: {v}" for k, v in item.items() if k != '_id'][:3]
                    response += f"{i}. {' | '.join(fields)}\n"
            else:
                response += f"{i}. {item}\n"
        
        if len(data) > 10:
            response += f"\n... and {len(data) - 10} more results"
        
        return response
    
    def _format_no_data_response(self, question):
        """Format no data response with suggestions"""
        response = "🔍 **No data found for your query.**\n\n"
        response += "💡 **Try these alternatives:**\n"
        
        if 'sales' in question.lower():
            response += "• 'total sales this year'\n• 'sales by city'\n• 'monthly sales trends'"
        elif 'customer' in question.lower():
            response += "• 'all customers'\n• 'top customers by spending'\n• 'customers by city'"
        elif 'product' in question.lower():
            response += "• 'all products'\n• 'top selling products'\n• 'worst performing products'"
        else:
            response += "• 'total sales'\n• 'customer count'\n• 'recent orders'"
        
        return response

# Global instance
enhanced_formatter = EnhancedResponseFormatter()

def format_enhanced_answer(question, raw_data):
    """Main function for enhanced response formatting"""
    return enhanced_formatter.format_enhanced_response(question, raw_data)