import requests
import json

myUrl = "http://localhost:8000/test?k=(keys)&r=r;s&page=0&num=5"
psabottools = "http://localhost:140/api/data_clean"

if __name__ == "__main__":
    with open('testQ.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for i in data[:1]:
        print(i)
        rq = {
            "version": 2,
            "content": i
        }
        s = requests.post(url=psabottools, json=rq)
        print(s.json())