import requests
import json


myUrl = "http://192.168.0.100:8000/test?k=(key)&r=r;s&page=0&num=10"
# psabottools = "http://localhost:140/api/data_clean"

if __name__ == "__main__":
    with open('data/testQ.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for k in list(data.keys()):
        print(data[k])
        keywords = "python;macos;"+data[k]
        s = requests.get(url=myUrl.replace("(key)", keywords))
        with open("data/" + k + ".json", 'w', encoding='utf-8') as fp:
            json.dump(s.json(), fp)
        fp.close()

    f.close()


