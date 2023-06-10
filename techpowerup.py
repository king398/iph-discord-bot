import os
from pymongo import MongoClient
import pandas as pd

## Initialising MongoDB connection, database, and collection.

print("Initialising MongoClient")
mongodb_connection_url = f"mongodb://root:{os.environ.get('MONGODB_PASSWORD')}@mongo/techpowerup?authSource=admin"
mongo_client = MongoClient(mongodb_connection_url)
database = mongo_client.get_database()

# CPU Collection
cpu_collection = database["CPU"]

# GPU Collection
gpu_collection = database["GPU"]



## CPU Class to provide CPU Object for embedding in Discord reply

class CPU():
    brand = ""
    name = ""
    def __init__(self, cpu: dict) -> None:
        pass



def searchcpu(query: dict):
    results = []
    search_query = {
        "Brand" : query["Brand"],
        "Name"  : {
            "$regex" : query["query"]
        }
    }
    documents = cpu_collection.find(search_query)
    for document in documents:
        results.append(document)
    if len(results) == 0:
        return False
    if len(results) == 1:
        return CPU(results[0])
    return(results)
