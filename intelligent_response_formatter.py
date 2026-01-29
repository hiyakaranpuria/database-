#!/usr/bin/env python3
"""
Intelligent Response Formatter - Enhanced response generation with business context
"""

from datetime import datetime
import re

class IntelligentResponseFormatter:
    def __init__(self):
        self.business_context = {
            'churn': 'customers who haven\'t ordered recently',
            'ltv': 'customer lifetime value',
            'seasonal': 'seasonal patterns and trends',
            'performance': 'business performance metrics'
        }
    
    def format_intelligent_response(self, question, raw_data, query_type=None):
        """Format response with business intelligence and context"""
        question_lower = question.lower()
        
        if isinstance(raw_data, str) and "Error" in raw_data:
            return self._format_error_with_suggestions(raw_data, question)
        
        if not isinstance(raw_data, list) or len(raw_data) == 0:
            return self._format_no_data_with_suggestions(question)
        
        # Detect response type based on data structure and question
        response_type = self._detect_response_type(raw_data, question_lower)
        
        if response_type == 'churn_analysis':
            return self._format_churn_analysis(raw_data, question)
        elif response_type == 'performance_analysis':
            return self._format_performance_analysis(raw_data, question)
        elif response_type == 'seasonal_analysis':
            return self._format_seasonal_analysis(raw_data, question)
        elif response_type == 'sales_summary':
            return self._format_sales_summary(raw_data, question)
        elif response_type == 'customer_analysis':
            return self._format_customer_analysis(raw_data, question)
        elif response_type == 'product_analysis':
            return self._format_product_analysis(raw_data, question)
        elif response_type == 'city_analysis':
            return self._format_city_analysis(raw_data, question)
        elif response_type == 'count_result':
            return self._format_count_result(raw_data, question)
        elif response_type == 'aggregation_result':
            return self._format_aggregation_result(raw_data, question)
        else:
            return self._format_generic_list(raw_data, question)
    
    def _detect_response_type(self, data, question):
        """Intelligently detect the type of response needed"""
        if not data:
            return 'no_data'
        
        first_item = data[0]
        
        # Check for churn analysis
        if 'daysSinceLastOrder' in str(first_item) or 'lastOrderDate' in str(first_item):
            return 'churn_analysis'
        
        # Check for seasonal analysis
        if 'monthName' in str(first_item) and 'totalSales' in str(first_item):
            return 'seasonal_analysis'
        
        # Check for performance analysis
        if ('productName' in str(first_item) or 'customerName' in str(first_item)) and 'totalSales' in str(first_item):
            return 'performance_analysis'
        
        # Check for city analysis
        if 'city' in str(first_item) and 'totalSales' in str(first_item):
            return 'city_analysis'
        
        # Check for sales summary
        if isinstance(first_item, dict) and len(first_item) <= 3 and any(key in ['totalSales', 'total'] for key in first_item.keys()):
            if any(word in question for word in ['sales', 'revenue', 'total']):
                return 'sales_summary'
        
        # Check for count results
        if isinstance(first_item, dict) and 'total' in first_item and len(first_item) == 1:
            return 'count_result'
        
        # Check for aggregation results
        if isinstance(first_item, dict) and '_id' in first_item and len(first_item) == 2:
            return 'aggregation_result'
        
        return 'generic_list'
    
    def _format_churn_analysis(self, data, question):
        """Format churn analysis results"""
        response = f"🚨 **Customer Churn Analysis**\n\n"
        response += f"Found **{len(data)}** customers who haven't ordered recently:\n\n"
        
        for i, customer in enumerate(data[:10], 1):
            name = customer.get('customerName', 'Unknown')
            days = int(customer.get('daysSinceLastOrder', 0))
            total_spent = customer.get('totalSpent', 0)
            orders = customer.get('totalOrders', 0)
            
            response += f"{i}. **{name}** - {days} days since last order\n"
            response += f"   💰 Total spent: ${total_spent:,.2f} ({orders} orders)\n\n"
        
        if len(data) > 10:
            response += f"... and {len(data) - 10} more at-risk customers\n\n"
        
        response += "💡 **Recommendation:** Consider reaching out with personalized offers to re-engage these customers."
        
        return response
    
    def _format_performance_analysis(self, data, question):
        """Format product/customer performance analysis"""
        question_lower = question.lower()
        
        if 'productName' in str(data[0]):
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
                response += f"   💰 Sales: ${sales:,.2f}\n"
                response += f"   📦 Units sold: {quantity:,}\n"
                response += f"   🛒 Orders: {orders:,}\n\n"
        
        elif 'customerName' in str(data[0]):
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
                response += f"   💰 Total spent: ${spent:,.2f}\n"
                response += f"   🛒 Orders: {orders} (avg: ${avg_order:.2f})\n\n"
        
        return response
    
    def _format_seasonal_analysis(self, data, question):
        """Format seasonal analysis results"""
        response = "📅 **Seasonal Sales Analysis**\n\n"
        
        total_sales = sum(item.get('totalSales', 0) for item in data)
        
        for item in data:
            month = item.get('monthName', 'Unknown')
            year = item.get('year', 'Unknown')
            sales = item.get('totalSales', 0)
            orders = item.get('orderCount', 0)
            avg_order = item.get('avgOrderValue', 0)
            
            percentage = (sales / total_sales * 100) if total_sales > 0 else 0
            
            response += f"📊 **{month} {year}**\n"
            response += f"   💰 Sales: ${sales:,.2f} ({percentage:.1f}% of total)\n"
            response += f"   🛒 Orders: {orders:,} (avg: ${avg_order:.2f})\n\n"
        
        # Find best and worst months
        if len(data) > 1:
            best_month = max(data, key=lambda x: x.get('totalSales', 0))
            worst_month = min(data, key=lambda x: x.get('totalSales', 0))
            
            response += f"🏆 **Best month:** {best_month.get('monthName')} (${best_month.get('totalSales', 0):,.2f})\n"
            response += f"📉 **Slowest month:** {worst_month.get('monthName')} (${worst_month.get('totalSales', 0):,.2f})\n"
        
        return response    def _for
mat_sales_summary(self, data, question):
        """Format sales summary with business context"""
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
        elif 'this month' in question_lower:
            time_context = " for this month"
        elif 'last month' in question_lower:
            time_context = " for last month"
        
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
    
    def _format_city_analysis(self, data, question):
        """Format city-wise analysis"""
        response = "🗺️ **Sales by Location**\n\n"
        
        total_sales = sum(item.get('totalSales', 0) for item in data)
        
        for i, item in enumerate(data, 1):
            city = item.get('city', item.get('_id', 'Unknown'))
            sales = item.get('totalSales', 0)
            orders = item.get('orderCount', 0)
            customers = item.get('customerCount', 0)
            
            percentage = (sales / total_sales * 100) if total_sales > 0 else 0
            
            response += f"{i}. **{city}**\n"
            response += f"   💰 Sales: ${sales:,.2f} ({percentage:.1f}%)\n"
            response += f"   🛒 Orders: {orders:,}\n"
            if customers > 0:
                response += f"   👥 Customers: {customers:,}\n"
            response += "\n"
        
        return response
    
    def _format_count_result(self, data, question):
        """Format count results with business context"""
        question_lower = question.lower()
        count = data[0].get('total', 0)
        
        # Determine what we're counting
        if 'customer' in question_lower:
            entity = 'customers'
            emoji = '👥'
        elif 'product' in question_lower:
            entity = 'products'
            emoji = '📦'
        elif 'order' in question_lower:
            entity = 'orders'
            emoji = '🛒'
        else:
            entity = 'records'
            emoji = '📊'
        
        response = f"{emoji} **{entity.title()} Count**\n\n"
        response += f"Total {entity}: **{count:,}**\n"
        
        # Add business context
        if entity == 'customers' and count > 1000:
            response += "\n🎯 Great customer base! Consider segmentation strategies."
        elif entity == 'orders' and count > 5000:
            response += "\n📈 High order volume! Strong business activity."
        
        return response
    
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
                elif 'max' in key.lower() or 'highest' in question_lower:
                    return f"📈 **Maximum Value:** ${value:,.2f}"
                elif 'min' in key.lower() or 'lowest' in question_lower:
                    return f"📉 **Minimum Value:** ${value:,.2f}"
                else:
                    return f"📊 **Result:** {value:,.2f}"
        
        return f"📊 **Result:** {first_item}"
    
    def _format_generic_list(self, data, question):
        """Format generic list results"""
        response = "📋 **Results:**\n\n"
        
        for i, item in enumerate(data[:10], 1):
            if isinstance(item, dict):
                # Format based on available fields
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
                    # Generic formatting
                    fields = [f"{k}: {v}" for k, v in item.items() if k != '_id'][:3]
                    response += f"{i}. {' | '.join(fields)}\n"
            else:
                response += f"{i}. {item}\n"
        
        if len(data) > 10:
            response += f"\n... and {len(data) - 10} more results"
        
        return response
    
    def _format_error_with_suggestions(self, error, question):
        """Format error messages with helpful suggestions"""
        response = f"❌ **Error:** {error}\n\n"
        response += "💡 **Suggestions:**\n"
        
        if 'no data' in error.lower():
            response += "• Try a different time period (e.g., 'last year', 'this month')\n"
            response += "• Check if the data exists in your database\n"
            response += "• Try a broader query (e.g., 'all sales' instead of specific filters)\n"
        
        response += "\n🔍 **Example queries:**\n"
        response += "• 'total sales this year'\n"
        response += "• 'top 10 customers'\n"
        response += "• 'products by sales'\n"
        
        return response
    
    def _format_no_data_with_suggestions(self, question):
        """Format no data response with suggestions"""
        response = "🔍 **No data found for your query.**\n\n"
        response += "💡 **Try these alternatives:**\n"
        
        if 'sales' in question.lower():
            response += "• 'total sales' (all time)\n"
            response += "• 'sales this year'\n"
            response += "• 'sales by city'\n"
        elif 'customer' in question.lower():
            response += "• 'all customers'\n"
            response += "• 'top customers by spending'\n"
            response += "• 'customers by city'\n"
        elif 'product' in question.lower():
            response += "• 'all products'\n"
            response += "• 'top selling products'\n"
            response += "• 'products by category'\n"
        else:
            response += "• 'total sales'\n"
            response += "• 'customer count'\n"
            response += "• 'recent orders'\n"
        
        return response

# Global instance
intelligent_formatter = IntelligentResponseFormatter()

def format_intelligent_answer(question, raw_data):
    """Main function for intelligent response formatting"""
    return intelligent_formatter.format_intelligent_response(question, raw_data)