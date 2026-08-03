import urllib.request
import urllib.parse
import json

def get_jobs():
    params = {
        "engine": "google_jobs",
        "q": "backend developer internship opening in pune and mumbai",
        "location": "maharashtra ",
        "hl": "en",
        "gl": "in",
        "api_key": "0a706d778b21094b2739b43703a80aee68d95c4492da768e95e18c59284578c9"
    }

    url = "https://serpapi.com/search.json?" + urllib.parse.urlencode(params)
    print(url.replace("0a706d778b21094b2739b43703a80aee68d95c4492da768e95e18c59284578c9", "***"))

    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=10) as response:
        res = json.loads(response.read().decode("utf-8"))
        jobs = res.get("jobs_results", [])
        print(f"Jobs found: {len(jobs)}")
        if res.get("error"):
            print(f"Error from API: {res['error']}")

get_jobs()
