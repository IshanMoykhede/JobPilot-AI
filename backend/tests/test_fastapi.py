import sys
import json
sys.path.append('.')

from fastapi.testclient import TestClient
from main import app
from app.dependencies.auth import get_current_user
from app.core.database import SessionLocal
from app.models.user import User
from app.models.candidate_profile import CandidateProfile  # FIX IMPORT ORDER

def test():
    db = SessionLocal()
    user = db.query(User).first()
    db.close()
    
    if not user:
        print("No user found in DB")
        return
        
    def override_get_current_user():
        return user
        
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    client = TestClient(app)
    
    print(f"Testing GET /api/resume/a762af22-9e79-431b-9043-2f124e9b058b for user {user.id}")
    try:
        response = client.get("/api/resume/a762af22-9e79-431b-9043-2f124e9b058b")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error during request: {e}")
        import traceback
        traceback.print_exc()
        
if __name__ == "__main__":
    test()
