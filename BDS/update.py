from pymongo import MongoClient
from urllib.parse import quote_plus

# MongoDB connection string
password = quote_plus(<actualpassword>)
MONGO_URI = f"mongodb+srv://<username>:{password}@<cluster>.jaheomk.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)

# Connect to DB and Collection
db = client['ecommerce_db']
collection = db['inventory'] # Collection name

update_result = collection.update_one(
    {"skus.inventory.skuId": "LIP-999"},
    {"$set": {"skus.$[].inventory.$[].quantity": 150}}
)
print("Modified document count:", update_result.modified_count)
