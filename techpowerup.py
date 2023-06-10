import os
from pymongo import MongoClient
import pandas as pd
import urllib.parse
## Initialising MongoDB connection, database, and collection.
print("Initialising MongoClient")
#mongodb_connection_url = f"mongodb://root:{os.environ.get('MONGODB_PASSWORD')}@mongo/techpowerup?authSource=admin"

# DEBUG MONGO HOST

mongodb_connection_url = f"mongodb://root:{os.environ.get('MONGODB_PASSWORD')}@localhost:4040/techpowerup?authSource=admin"

client = MongoClient(mongodb_connection_url)

database = client.get_database()

# CPU Collection
cpu_collection = database["CPU"]

# GPU Collection
gpu_collection = database["GPU"]



## CPU Class to provide CPU Object for embedding in Discord reply

class CPU():
    brand = ""
    name = ""
    link = ""
    codename = ""
    cores = ""
    clock = ""
    socket = ""
    process = ""
    l3cache = ""
    tdp = ""
    released = ""
    def __init__(self, cpu: dict) -> None:
        self.brand = cpu["Brand"]
        self.name = cpu["Name"]
        self.link = cpu["Link"]
        self.codename = cpu["Codename"]
        self.cores = cpu["Cores"]
        self.clock = cpu["Clock"]
        self.socket = cpu["Socket"]
        self.process = cpu["Process"]
        self.l3cache = cpu["L3 Cache"]
        self.tdp = cpu["TDP"]
        self.released = cpu["Released"]



def searchcpu(query: dict):
    results = []
    search_query = {"Brand" : query["Brand"]}
    search_query.update({
            "Name"  : {
                "$regex" : query['query']+".{2,3}$"
            }
        })
    documents = cpu_collection.find(search_query)
    for document in documents:
        results.append(document)
    if len(results) == 1:
        return CPU(results[0])
    if len(results) == 0:
        return False
    return(results)
