#!/usr/bin/env python
import os
import requests
from flask import Flask, jsonify, request
from flasgger import Swagger
import configparser

# set config
# config = configparser.ConfigParser()
# config.read('~/.config/config')
# reddit = config.get('api_url', 'REDDIT_API')
# stack_overflow = config.get('api_url', 'STACKOVERFLOW_API')
reddit = "http://localhost:100"
stack_overflow = "http://localhost:80"

# set flask & swagger
app = Flask(__name__)
app.config['SWAGGER'] = {
    "title": "Data Controller Service",
    "description": "API for Reddit data collection & retrieval",
    "version": "1.0",
    "termsOfService": "",
    "hide_top_bar": True
}
swagger = Swagger(app=app, template_file="swagger_doc.yml")


# search only, return urls
@app.route('/hello', methods=['GET'])
def hello():
    return "hello world"


# search only, return urls
@app.route('/test', methods=['GET'])
def get_data():
    # Get parameters
    keywords = request.values.get('k')
    resources = request.values.get('r')
    page = request.values.get('page')
    result_num = request.values.get('num')
    print("hi")
    try:
        # Generate lists
        keywords = keywords.split(";")
        resources = resources.split(";")
        my_rq = {
            "keywords": keywords,
            "page_num": int(page),
            "result_num": int(result_num)
        }
        # collect data
        result = []
        if "s" in resources:
            print("collect from so")
            s = requests.session()
            s.keep_alive = False
            resp = s.post(url=stack_overflow+"/retrieve", json=my_rq).json()
            for posts in resp:
                posts["resource"] = "StackOverflow"
            result += resp
        """
        if "r" in resources:
            print("collect from reddit")
            s = requests.session()
            s.keep_alive = False
            resp = s.post(url=reddit+"/retrieve", json=my_rq).json()
            for posts in resp:
                posts["resource"] = "Reddit"
            result += resp
        """
        response = {"result": result}
    except Exception as e:
        response = {"error": e.__class__.__name__ + " : " + e.args[0]}
    return jsonify(response)


if __name__ == "__main__":
    print("Welcome to Data Controller service ~~")
    app.run(host='0.0.0.0', port=os.environ.get("FLASK_SERVER_PORT", 8000), debug=True)
