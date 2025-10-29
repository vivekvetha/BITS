from pymongo import MongoClient
from urllib.parse import quote_plus

# MongoDB connection string
password = quote_plus(<actualpassword>)
MONGO_URI = f"mongodb+srv://<username>:{password}@<cluster>.jaheomk.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)

# Connect to DB and Collection
db = client['ecommerce_db']
collection = db['inventory'] # Collection name

read_result = collection.find_one({"skus.inventory.skuId": "LIP-999"})
print("Read result:", read_result)
