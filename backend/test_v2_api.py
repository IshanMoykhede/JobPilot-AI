import sys
import os
import uuid
import json
from fastapi.testclient import TestClient

# Ensure the backend directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.candidate_insights import CandidateInsights
from app.dependencies.auth import get_current_user
from app.resume_tailoring_agent_v2.checkpointer import get_checkpointer

print("Setting up test...")

db = SessionLocal()

from app.models.candidate_profile import CandidateProfile

# 1. Find or create a test user
user = db.query(User).filter(User.email == "test_v2_user@example.com").first()
if not user:
    user = User(
        id=uuid.uuid4(),
        name="Test V2 User",
        email="test_v2_user@example.com",
        password_hash="fakehash"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

# 2. Ensure user has CandidateProfile and Insights
profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
if not profile:
    profile = CandidateProfile(id=uuid.uuid4(), user_id=user.id, profile_json={})
    db.add(profile)
    db.commit()
    db.refresh(profile)

insights = db.query(CandidateInsights).filter(CandidateInsights.candidate_profile_id == profile.id).first()
if not insights:
    insights = CandidateInsights(
        id=uuid.uuid4(),
        candidate_profile_id=profile.id,
        artifact_type="CANDIDATE_KNOWLEDGE",
        artifact_json={
            "experience": [{"title": "Software Developer", "company": "Tech Corp"}],
            "education": [{"degree": "B.Sc Computer Science", "university": "MIT"}]
        }
    )
    db.add(insights)
    db.commit()

# 3. Override FastAPI dependencies
def override_get_current_user():
    return user

app.dependency_overrides[get_current_user] = override_get_current_user

# 4. Initialize TestClient
client = TestClient(app)

# 5. Run Tests
print("\n--- TEST 1: POST /api/v2/resume/start ---")
start_payload = {
    "title": "My V2 Backend Test Resume",
    "message": "Draft my resume based on this job description."
}
start_response = client.post("/api/v2/resume/start", json=start_payload)
print(f"Status Code: {start_response.status_code}")
if start_response.status_code != 200:
    print(f"Error: {start_response.text}")
    sys.exit(1)
    
data = start_response.json()
resume_id = data["resume_id"]
print(f"Successfully started session! Resume ID: {resume_id}")
print(f"Initial AI Reply: {data.get('messages', [{}])[-1].get('content')}")
print(f"Initial Draft Keys Generated: {list(data.get('drafts', {}).keys())}")
print(f"Pending Sections Remaining: {data.get('pending_sections')}")

print("\n--- TEST 2: Simulate User sending 'next' 3 times to generate more sections ---")
for i in range(3):
    print(f"\n--- Turn {i+1} ---")
    chat_payload = {"message": "Looks good! Next."}
    print(f"Sending message: '{chat_payload['message']}'...")
    chat_response = client.post(f"/api/v2/resume/{resume_id}/chat", json=chat_payload)
    
    if chat_response.status_code == 200:
        data = chat_response.json()
        print(f"AI Reply: {data.get('reply')}")
        print(f"Draft Keys Generated So Far: {list(data.get('drafts', {}).keys())}")
        print(f"Pending Sections Remaining: {data.get('pending_sections')}")
    else:
        print(f"Error: {chat_response.text}")
        sys.exit(1)

print(f"\n--- TEST 3: GET /api/v2/resume/{resume_id} ---")
get_response = client.get(f"/api/v2/resume/{resume_id}")
print(f"Status Code: {get_response.status_code}")
if get_response.status_code == 200:
    data = get_response.json()
    print(f"Resume Title: {data['title']}")
    print(f"Resume Status: {data['status']}")
    print(f"Total Chat Messages: {len(data['messages'])}")
    print(f"All Draft Sections: {list(data['drafts'].keys())}")
else:
    print(f"Error: {get_response.text}")

print("\nAll endpoints tested successfully!")
