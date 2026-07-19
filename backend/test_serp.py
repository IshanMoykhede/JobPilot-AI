import urllib.request
import urllib.parse
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("SERPAPI_API_KEY")

params = {
    "engine": "google_jobs",
    "q": "Backend developer internship",
    "api_key": api_key
}

url = "https://serpapi.com/search.json?" + urllib.parse.urlencode(params)

try:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=10) as response:
        res = json.loads(response.read().decode("utf-8"))
        print(f"SUCCESS! Jobs found: {len(res.get('jobs_results', []))}")
except Exception as e:
    print(f"ERROR: {e}")
    if hasattr(e, 'read'):
        print(e.read().decode('utf-8'))
