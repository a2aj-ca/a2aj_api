from fastapi import FastAPI
import os
from pymongo import MongoClient

# Check if production or development
if os.getenv("MONGO_DB") == None:
    DB_URL = "mongodb.railway.internal"
else:
    DB_URL = os.getenv("MONGO_DB")

# Connect to MongoDB
client = MongoClient(DB_URL)
db = client["test"]
collection = db['decisions']

app = FastAPI()

@app.get("/")
async def root():
    # return items in collection
    items = collection.find()
    items_list = []
    for item in items:
        items_list.append(item)
    return items_list
    