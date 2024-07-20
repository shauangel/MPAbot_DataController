import datetime
import json
from pymongo import MongoClient
from bson import json_util

client = MongoClient("mongodb://datacontroller-mongo:27017/datacontroller_db")
# temp_client = MongoClient("mongodb://localhost:50001/")
DB = client["DataController"]
UNIFIED_DATA_COLLECTION = DB["UnifiedData"]
QUESTION_COLLECTION = DB["Questions"]


# query searched question list
def query_question(question):
    try:
        query = {"question": question}
        result = QUESTION_COLLECTION.find_one(query)
    except Exception as e:
        print(e.__context__)
    return json.loads(json_util.dumps(result))


# insert searched questions
def insert_question(question, links):
    try:
        insert_id = QUESTION_COLLECTION.insert_one({"question": question,
                                                    "links": links})
    except Exception as e:
        print(e.__context__)
    return str(insert_id)


# query multiple posts by links
def query_posts_by_links(link_list):
    try:
        query = {"link": {"$in": link_list}}
        cursor = UNIFIED_DATA_COLLECTION.find(query)
        result = [r for r in cursor]
    except Exception as e:
        return {"Error": e}
    return json.loads(json_util.dumps(result))


# insert multiple posts
def insert_posts(posts):
    # Step 1: add date
    for p in posts:
        p["saved_time"] = datetime.datetime.utcnow()
    inserted_ids = UNIFIED_DATA_COLLECTION.insert_many(posts)
    return str(inserted_ids)


# remove object id
def remove_obj_id(data):
    result = []
    for d in data:
        try:
            d.pop("_id")
            result.append(d)
        except KeyError:
            print("no _id")
            result.append(d)
    return result


if __name__ == "__main__":
    question = "What"
    test = query_question(question)
    print(type(test))
    print(test)