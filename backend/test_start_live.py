import requests
import json
import sys

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMTE5Nzg2Zi0zN2M0LTQ1ODktYTk5Yy1hY2E1MzM0N2Q0NmMiLCJleHAiOjE3ODU4NTUyMjZ9.nLE_NelvOoJAEorpTZ4kK9lf-H9e4wqr6SWprLNDjBc"
job_id = "041bfb8b-ecc3-4ac1-8abe-b93876c6f936"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "title": "Simulation Test Resume",
    "job_id": job_id,
    "message": "generate my resume"
}

print("Calling POST /api/v2/resume/start API...")
try:
    response = requests.post("http://localhost:8000/api/v2/resume/start", headers=headers, json=payload)
    
    with open("start_result.json", "w", encoding="utf-8") as f:
        if response.status_code == 200:
            json.dump(response.json(), f, indent=4)
            print("✅ Success! Response saved to start_result.json")
            print(f"Resume ID: {response.json().get('resume_id')}")
        else:
            f.write(f"Error {response.status_code}:\n{response.text}")
            print(f"❌ Error {response.status_code}! Output saved to start_result.json")
except Exception as e:
    print(f"Failed to connect: {e}")
