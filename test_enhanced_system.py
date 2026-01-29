#!/usr/bin/env python3
"""
Test the enhanced AI database system
"""

from enhanced_query_engine import generate_enhanced_query
from dynamic_query_executor import execute_mongo_query
from enhanced_response_formatter import format_enhanced_answer

def test_enhanced_system():
    """Test all enhanced queries"""
    questions = [
        'total sales this year',
        'customers who haven\'t ordered recently',
        'which products sold least', 
        'show me seasonal sales patterns',
        'top 5 customers by spending'
    ]

    print('🚀 Testing Enhanced AI Database System')
    print('=' * 50)

    for question in questions:
        print(f'\n💬 Question: "{question}"')
        try:
            query_str = generate_enhanced_query(question)
            raw_results = execute_mongo_query(query_str, question)
            
            if raw_results:
                response = format_enhanced_answer(question, raw_results)
                print(f'✅ Success ({len(raw_results)} results)')
                print(f'📊 Response: {response[:200]}...')
            else:
                print('❌ No results returned')
                
        except Exception as e:
            print(f'❌ Error: {e}')

    print('\n🎉 Enhanced system testing complete!')

if __name__ == "__main__":
    test_enhanced_system()