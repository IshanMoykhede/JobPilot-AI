import urllib.request
import urllib.parse
import json

api_key = "0a706d778b21094b2739b43703a80aee68d95c4492da768e95e18c59284578c9"

params = {
    "engine": "google_jobs",
    "q": "software engineering jobs in pune",
    "location": "Pune, Maharashtra, India",
    "api_key": api_key,
}

url = "https://serpapi.com/search.json?" + urllib.parse.urlencode(params)

print("Calling SerpAPI directly via HTTPS request...")
try:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=30) as response:
        results = json.loads(response.read().decode("utf-8"))
        
        # Save results to a json file
        with open("serp_response.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        print("Search completed. Response saved to serp_response.json")
except Exception as e:
    print(f"Error calling SerpAPI: {e}")
