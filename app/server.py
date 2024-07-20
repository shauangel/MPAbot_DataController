#!/usr/bin/env python
import os
import time

from models import db_manager as db
from models.data_unifier import UnifiedData
import requests
from flask import Flask, jsonify, request
from flasgger import Swagger


# Registered Services
sources_url = {
    "stackoverflow": "http://so-parser-backend:9091",
    "reddit": "http://reddit-parser-backend:9090",
    "codeproject": "http://codeproject-parser-backend:9095"
}

# set app & swagger
app = Flask(__name__)
app.config['SWAGGER'] = {
    "title": "Data Controller Service",
    "description": "API for Reddit data collection & retrieval",
    "version": "1.0",
    "termsOfService": "",
    "hide_top_bar": True
}
swagger = Swagger(app=app, template_file="swagger_doc.yml")


# TESTER~
@app.route('/insert', methods=['GET'])
def test():
    test_id = db.collection.insert_one({"test": "test"}).inserted_id
    print(test_id)
    return str(test_id)


# search only, return urls
@app.route('/data', methods=['GET'])
def get_data():
    # Step 1: Get parameters
    keywords = request.values.get('keywords')
    question = request.values.get('question')
    sources = request.values.get('resources')
    page = request.values.get('page')
    result_num = request.values.get('num')

    try:
        # Step 1: Get requested source list
        sources = sources.split(";")
        print(f"<<Step 1>> Receive Parameters\n "
              f"Keywords: {keywords}\n"
              f"Question: {question}\n"
              f"Sources: {sources}\n"
              f"Page: {page}\n Result Number: {result_num}")
        print("---"*10)

        # Step 2: Search Question in db
        result = db.query_question(question)
        if result is None:
            # Step 3: Search from Google
            links = {}
            for s in sources:
                resp = requests.get(sources_url[s] + f"/search?keywords={keywords+';'+question}"
                                                     f"&page={page}&num={result_num}").json()
                links[s] = resp["result"]
            print(f"<<Step 2>> Search for related links\n{links}")
            print("---" * 10)
            db.insert_question(question, links=links)
        else:
            links = result['links']

        # Step 4: Check database
        retrieve = []
        try:
            results_from_db = db.query_posts_by_links(sum(links.values(), []))
            print(results_from_db)
            retrieve += results_from_db
            # Generate link list needed to scrape
            for d in retrieve:
                links[d['source']].remove(d['link'])
        except Exception as e:
            print(e.__context__)
        print(f"<<Step 3>> Query database\n{retrieve}")
        print("---" * 10)

        # Step 5: Retrieve information from each parsing service
        print(f"<<Step 4>> Retrieve information")
        data_from_services = []
        for s in sources:
            request_url = sources_url[s] + "/retrieve"
            print(f"Collecting data from {s}...")
            print(request_url)
            resp = requests.post(url=request_url, json={"links": links[s]}, timeout=30).json()
            for r in resp:
                r['source'] = s
            data_from_services += resp
            print(resp)
        print("---"*10)

        if len(data_from_services) > 0:
            # Step 6: Unify data
            print(f"<<Step 5>> Unifying data")
            for d in data_from_services:
                unifier = UnifiedData(d)
                d = unifier.get_result()
                retrieve.append(d)
            print(data_from_services)
            print("---"*10)
            # response = {"result": data_from_services}

            # Step 7: Insert new posts
            print(f"<<Step 6>> Store data into database")
            insert_id = db.insert_posts(data_from_services)
            print(insert_id)
            print("---"*10)
        else:
            print("<<Step 5-2>> No new data needed~~ skip requests")

        # Step 8: Retrieve information
        result = db.remove_obj_id(retrieve+data_from_services)
        response = {"result": result}

    except Exception as e:
        response = {"error": e.__class__.__name__ + " : " + e.args[0]}
    return jsonify(response)


if __name__ == "__main__":
    print("Welcome to Data Controller service ~~")
    app.run(host='0.0.0.0', port=os.environ.get("FLASK_SERVER_PORT", 8000), debug=True)
