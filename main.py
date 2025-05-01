from fastapi import FastAPI
import os
from pymongo import MongoClient

# Check if production or development
if os.getenv("MONGO_DB") == None:
    # MongoDB is not set in Railway
    # Get the MongoDB URL from the environment variable in Railway
    DB_URL = os.getenv("MONGO_URL")
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
    