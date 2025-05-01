from fastapi import FastAPI, Body
import os
from pymongo import MongoClient
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Check if var is in the environment
# MONGO_DB is local, MONGO_URL is production
DB_URL = os.getenv("MONGO_DB") or os.getenv("MONGO_URL")

# Connect to MongoDB
client = MongoClient(DB_URL)
db = client["test"]
collection = db['decisions']

# Create FastAPI app
app = FastAPI()

# Pydantic model for the decision
class Decision(BaseModel):
    citation: str
    citation2: Optional[str] = None
    dataset: str
    year: int
    name: str
    language: str
    document_date: str
    source_url: str
    scraped_timestamp: Optional[str] = None
    unofficial_text: Optional[str] = None
    other: Optional[Dict[str, Any]] = None

# Hello world
@app.get("/")
def root():
    # return items in collection
    items = collection.find()
    items_list = []
    for item in items:
        items_list.append(item['text'])
    return items_list

@app.post("/decisions/", status_code=201)
def create_decision(decision: Decision = Body(...)):
    # Insert the decision into the collection
    result = collection.insert_one(decision.dict())
    # Return the created document with its ID
    return {
        "id": str(result.inserted_id),
        "message": f"Decision '{decision.name}' created successfully",
        "citation": decision.citation
    }