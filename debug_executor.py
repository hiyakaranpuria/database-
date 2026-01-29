from dynamic_query_executor import executor
import json
from bson import json_util

# Test the executor with a simple query
question = 'total sales'
query_str = '[{"$match": {"status": "completed"}}, {"$group": {"_id": null, "total": {"$sum": "$amount"}}}]'

print("Question:", question)
print("Query string:", query_str)

try:
    # Parse the query
    query_data = json.loads(query_str, object_hook=json_util.object_hook)
    print("Parsed query:", query_data)
    
    # Determine collection
    collection_name = executor._determine_collection(question, query_str)
    print("Collection determined:", collection_name)
    
    # Execute directly on collection
    collection = executor.db[collection_name]
    results = list(collection.aggregate(query_data))
    print("Direct aggregation results:", results)
    
    # Test the full executor method
    full_result = executor.execute_query(query_str, question)
    print("Full executor result:", full_result)
    
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()