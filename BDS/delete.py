from pymongo import MongoClient
from urllib.parse import quote_plus

# MongoDB connection string
password = quote_plus(<actualpassword>)
MONGO_URI = f"mongodb+srv://<username>:{password}@<cluster>.jaheomk.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)

# Connect to DB and Collection
db = client['ecommerce_db']
collection = db['inventory'] # Collection name

delete_result = collection.delete_one({"skus.inventory.skuId": "LIP-999"})
print("Deleted document count:", delete_result.deleted_count)
