import json
import time

import requests

data_controllor_url = "http://localhost:200"

if __name__ == "__main__":
    with open("samples.json", "r", encoding="utf-8") as file:
        sample_q = json.load(file)
    file.close()

    category = list(sample_q.keys())
    cat = category[6]
    count = 1
    print(f"Category: {cat}")
    for q in sample_q[cat]:
        print(f"Q{count}: {q}")
        start = time.time()
        url = data_controllor_url + f"/data?keywords=python&question={q}" \
                                    f"&resources=stackoverflow;reddit;codeproject" \
                                    f"&page=0&num=10"
        resp = requests.get(url, timeout=100).json()
        print(resp)
        end = time.time()
        print(f"Retrieve time: {end-start}")
        with open(f"result/{cat}_Q{count}.json", 'w', encoding='utf-8') as file:
            json.dump(fp=file, obj=resp)
        file.close()
        count += 1
        print("---"*10)


