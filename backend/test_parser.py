import urllib.request
import urllib.parse
import json

def test(query):
    print(f"--- Query: {query} ---")
    url = "http://127.0.0.1:8000/agent/test-serp?query=" + urllib.parse.quote(query)
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=30) as response:
            res = json.loads(response.read().decode("utf-8"))
            print(f"Role: {res.get('parsed_role')}")
            print(f"Location: {res.get('parsed_location')}")
            print(f"Jobs: {res.get('jobs_count')}")
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'read'):
            print(e.read().decode('utf-8'))

test("Backend Developer Pune")
test("Backend Developer Internship Pune")
test("Data Scientist Bangalore")
test("Mechanical Engineer Chennai")
