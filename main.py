from fastapi import FastAPI, Body
import os
from pymongo import MongoClient
from typing import Optional, List, Dict, Any, Union

# Check if var is in the environment
# MONGO_DB is local, MONGO_URL is production
DB_URL = os.getenv("MONGO_DB") or os.getenv("MONGO_URL")

# Connect to MongoDB
client = MongoClient(DB_URL)
db = client["test"]
collection = db['decisions']

# Create FastAPI app
app = FastAPI()

# Hello world
@app.get("/")
def root():
    # return items in collection
    num_items = collection.count_documents({})
    return f'There are {num_items} items in the collection.'

# list all decisions
@app.get("/decisions/")
def list_decisions():
    # Get all documents in the collection
    decisions = list(collection.find({}, {"citation": 1, "name": 1, "dataset": 1, "document_date": 1, "_id": 0}))
    return decisions

# list tribunals
@app.get("/list_tribunals/")
def list_tribunals():
    # Get all unique values of the "dataset" field
    tribunals = collection.distinct("dataset")
    return tribunals

# get a single decision
@app.get("/decisions/name/{decision_name}")
def get_decision(decision_name: str):
    # Find the decision by name
    decision = collection.find_one({"name": decision_name})
    if decision:
        # Remove the "_id" field from the result
        decision.pop("_id", None)
        return decision
    else:
        return {"message": f"Decision '{decision_name}' not found"}

# get a single decision by citation
@app.get("/decisions/citation/{citation}")
def get_decision_by_citation(citation: str):
    # Find the decision by citation
    decision = collection.find_one({"citation": citation})
    if decision:
        # Remove the "_id" field from the result
        decision.pop("_id", None)
        return decision
    else:
        return {"message": f"Decision with citation '{citation}' not found"}

@app.post("/upload/", status_code=201)
def create_decision(data: dict = Body(...)):
    # Insert whatever JSON is provided directly into MongoDB
    result = collection.insert_one(data)
    
    # Return the created document with its ID
    return {
        "id": str(result.inserted_id),
        "message": "Document created successfully"
    }