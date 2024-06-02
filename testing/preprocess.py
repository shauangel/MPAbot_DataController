import requests
import json

url= "http://localhost:140/api/data_clean"
myjson = {
    "version": 2,
    "content": ""
}

with open('data/testQ.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

result = {}
for k in list(data.keys()):
    myjson["content"] = data[k]
    resp = requests.post(url=url, json=myjson).json()
    result[k] = resp["token"]

with open('data/testQ_processed.json', 'w', encoding='utf-8') as f:
    json.dump(result, f)

