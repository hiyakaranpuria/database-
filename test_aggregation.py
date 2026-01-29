from pymongo import MongoClient
from bson import json_util
import json

client = MongoClient('mongodb://localhost:27017')
db = client['ai_test_db']

# Test simple aggregation
print("Testing simple aggregation...")
pipeline = [
    {"$match": {"status": "completed"}},
    {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
]

results = list(db.orders.aggregate(pipeline))
print("Results:", results)

# Test the query generator output
from dynamic_query_generator import generate_mongo_query
from dynamic_query_executor import execute_mongo_query

print("\nTesting query generator...")
question = "total sales"
query_str = generate_mongo_query(question)
print("Generated query:", query_str)

# Parse and execute
query_data = json.loads(query_str, object_hook=json_util.object_hook)
print("Parsed query:", query_data)

results = list(db.orders.aggregate(query_data))
print("Aggregation results:", results)