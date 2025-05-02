# A2AJ API
Use this API to upload and access decisions in the RLL Bulk Dataset.

## How to use
- Run locally using `hypercorn main:app --reload`
- Run on codespaces: python -m hypercorn main:app --reload

## How to insert a document

### Insert a single document

Current behaviour: 
- uploads document (json must match schema in RLL bulk dataset), checks if it exists in the dataset, if it does not, inserts it.
- only can upload one decision at a time

import requests

url = "https://a2ajapi-production.up.railway.app/decisions/"
res = requests.post(url, json.loads(sample)[0])

print(res.status_code)


