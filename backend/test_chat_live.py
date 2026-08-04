import requests
import json
import sys

if len(sys.argv) < 2:
    print("Please provide a message. Example: python test_chat_live.py \"Please generate my summary section now\"")
    sys.exit(1)

message = sys.argv[1]

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMTE5Nzg2Zi0zN2M0LTQ1ODktYTk5Yy1hY2E1MzM0N2Q0NmMiLCJleHAiOjE3ODU4NTUyMjZ9.nLE_NelvOoJAEorpTZ4kK9lf-H9e4wqr6SWprLNDjBc"

# We use the resume_id generated from the previous start API call
resume_id = "b6b059cd-a36c-45d1-b753-160969dc6264"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "message": message
}

print(f"Calling POST /api/v2/resume/{resume_id}/chat with message: '{message}'")
try:
    response = requests.post(f"http://localhost:8000/api/v2/resume/{resume_id}/chat", headers=headers, json=payload)
    
    with open("chat_result.json", "w", encoding="utf-8") as f:
        if response.status_code == 200:
            json.dump(response.json(), f, indent=4)
            print("Success! Response saved to chat_result.json")
            
            # Print the AI's reply to the console for quick viewing
            reply = response.json().get('reply')
            print(f"\n🤖 AI Reply: {reply}")
        else:
            f.write(f"Error {response.status_code}:\n{response.text}")
            print(f"Error {response.status_code}! Output saved to chat_result.json")
except Exception as e:
    print(f"Failed to connect: {e}")
