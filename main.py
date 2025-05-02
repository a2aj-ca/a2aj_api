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

# helper function to check all of the citation fields
def search_citation(citation: str):
    # Find the decision by citation
    decision = collection.find_one({"citation_en": citation})
    if decision:
        return decision
    elif collection.find_one({"citation_en": citation}):
        return collection.find_one({"citation_en": citation})
    elif collection.find_one({"citation_fr": citation}):
        return collection.find_one({"citation_fr": citation})
    elif collection.find_one({"citation": citation}):
        return collection.find_one({"citation": citation})
    else:
        return None


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
    decisions = list(collection.find({}, {"citation_en": 1, "citation2_en": 1, "citation_fr":1, "citation2_fr":1, "name_en": 1, "name_fr":1, "dataset": 1, "document_date_en": 1, "docuemt_date_fr":1, "_id": 0}))
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
    entry = collection.find_one({"name": decision_name})
    if entry:
        # check if the entry has a num_download field, create it if it doesn't, and update the collection
        if 'num_download' in entry:
            # if it does, increment it by 1
            entry['num_download'] += 1
            collection.update_one({"_id": entry["_id"]}, {"$set": {"num_download": entry['num_download']}})
        else:
            # if it doesn't, create it and set it to 1
            entry['num_download'] = 1
            collection.update_one({"_id": entry["_id"]}, {"$set": {"num_download": 1}})
        # Remove the "_id" field from the result before returning
        entry.pop("_id", None)
        return entry
    else:
        return {"message": f"Decision '{decision_name}' not found"}

# get a single decision by citation
@app.get("/decisions/citation/{citation}")
def get_decision_by_citation(citation: str):
    entry = search_citation(citation)
    if entry == None:
        return {"message": f"Decision with citation '{citation}' not found"}
    else:
        entry.pop("_id", None)
        return entry

# takes an entry and checks whether it meets minimum data model requirements
# checks whether the entry exists in the database
# if it does not, creates the entry
# if it does, updates the entry
@app.post("/upload/", status_code=201)
def create_decision(data: dict = Body(...)):
    # Define required fields
    required_name = ('name_en' in data or 'name_fr' in data)
    required_citation = ('citation_en' in data or 'citation_fr' in data)
    required_dataset = ('dataset' in data)
    required_text = ('unofficial_text_en' in data or 'unofficial_text_fr' in data)

    # Check if all required fields are present
    if not (required_name and required_citation and required_dataset and required_text):
        return {"message": "Missing required fields: name, citation, dataset, or text"}
    
    # check if the entry already exists
    search_res = search_citation(data.get('citation_en', data.get('citation_fr', data.get('citation2_en', data.get('citation2_fr')))))
    if search_res == None:
        new_entry = collection.insert_one(data.to_dict())
        return {
            "id": str(new_entry.inserted_id),
            "message": "Document created successfully"
        }
    else:
        collection.update_one(
            {"_id": search_res["_id"]},
            {"$set": data}
        )
        return {
            "id": str(search_res["_id"]),
            "message": "Document updated successfully"
        }
    
# upload v2
@app.post("/upload_v2/", status_code=201)
def upload_decision(data: dict = Body(...)):
    # Define required fields
    name = data.get('name')
    citation = data.get('citation')
    dataset = data.get('dataset')
    language = data.get('language')

    # Check if all required fields are present
    if not (name and citation and dataset and language):
        return {"message": "Missing required fields: name, citation, dataset, or language"}
    
    # transform the data to the correct format
    # rename each key to include _en or _fr, depending on the language
    transformed_data = {}
    for key in data.keys():
        if key == 'language':
            continue
        if key == 'dataset':
            transformed_data['dataset'] = data[key]
            continue
        transformed_data[f'{key}_{language}'] = data[key]
    
    # check if the entry already exists
    search_res = search_citation(transformed_data.get('citation_en', transformed_data.get('citation_fr', transformed_data.get('citation2_en', transformed_data.get('citation2_fr')))))
    if search_res != None:
        collection.update_one(
            {"_id": search_res["_id"]},
            {"$set": transformed_data}
        )
        return {
            "id": str(search_res["_id"]),
            "message": "Document updated successfully"
        }
    else:
        # check if the entry exists, but was uploaded in a different language
        if 'SCR' in citation:
            citation = citation.replace('SCR', 'RCS')
        elif 'RCS' in citation:
            citation = citation.replace('RCS', 'SCR')
        elif 'SCC' in citation:
            citation = citation.replace('SCC', 'CSC')
        elif 'CSC' in citation:
            citation = citation.replace('CSC', 'SCC')
        
        search_res = search_citation(citation)
        if search_res != None:
            collection.update_one(
                {"_id": search_res["_id"]},
                {"$set": transformed_data}
            )
            return {
                "id": str(search_res["_id"]),
                "message": "Document updated successfully"
            }
        else:
            # new entry
            new_entry = collection.insert_one(transformed_data)
            return {
                "id": str(new_entry.inserted_id),
                "message": "Document created successfully"
            }