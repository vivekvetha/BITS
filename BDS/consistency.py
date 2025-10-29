from pymongo import MongoClient
from pymongo.write_concern import WriteConcern
from pymongo.read_concern import ReadConcern
from urllib.parse import quote_plus
import time

# MongoDB connection string
password = quote_plus(<actualpassword>)
MONGO_URI = f"mongodb+srv://<username>:{password}@<cluster>.jaheomk.mongodb.net/?retryWrites=true&w=majority"

def test_rw_performance(wc, rc, label):
    client = MongoClient(MONGO_URI)
    collection = client["ecommerce_db"].get_collection(
        "inventory",
        write_concern=wc,
        read_concern=rc
    )

    print(f"\nTesting: {label}")

    # WRITE
    write_start = time.time()
    collection.insert_one({
        "type": "test",
        "skus": [{"skuType": "perfume", "inventory": [{"skuId": f"TEST-{label}", "quantity": 1}]}]
    })
    write_end = time.time()
    print(f"Write time: {write_end - write_start:.5f} sec")

    # READ
    read_start = time.time()
    doc = collection.find_one({ "skus.inventory.skuId": f"TEST-{label}" })
    read_end = time.time()
    print(f"Read time: {read_end - read_start:.5f} sec")

# Run tests
test_rw_performance(WriteConcern(w=1), ReadConcern("local"), "W1-RLocal")
test_rw_performance(WriteConcern("majority", wtimeout=1000), ReadConcern("majority"), "WMajority-RMajority")
test_rw_performance(WriteConcern(w=1), ReadConcern("available"), "W1-RAvailable")
