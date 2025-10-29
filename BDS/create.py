from pymongo import MongoClient
from urllib.parse import quote_plus

# MongoDB connection string
password = quote_plus(<actualpassword>)
MONGO_URI = f"mongodb+srv://<username>:{password}@<cluster>.jaheomk.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)

# Connect to DB and Collection
db = client['ecommerce_db']
collection = db['inventory'] # Collection name

new_product = {
    "type": "cosmetics",
    "skus": [
        {
            "skuType": "lipstick",
            "inventory": [
                {
                    "skuId": "LIP-999",
                    "retailerId": "NYKAA007",
                    "retailerName": "Nykaa",
                    "maxRetailPrice": 249.99,
                    "averageRating": 4.7,
                    "variant": "matte",
                    "shade": "cherry red",
                    "quantity": 100
                }
            ]
        }
    ]
}

insert_result = collection.insert_one(new_product)
print("Inserted document ID:", insert_result.inserted_id)
