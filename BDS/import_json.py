import json
from pymongo import MongoClient
from urllib.parse import quote_plus

# MongoDB connection string
password = quote_plus(<actualpassword>)
MONGO_URI = f"mongodb+srv://<username>:{password}@<cluster>.jaheomk.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)

# Connect to DB and Collection
db = client['ecommerce_db']
orders_collection = db['inventory'] # Collection name

# Load JSON file
with open('ecommerce_data.json', encoding='utf-8') as f:
    data = json.load(f)

# Insert into collection
orders_collection.insert_many(data)
print("Inserted", len(data), "orders into MongoDB.")
