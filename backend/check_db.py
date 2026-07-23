import sys
import os
import json
sys.path.append(r"c:\Users\igmoy\OneDrive\Desktop\JobPilot AI\backend")

from app.database import SessionLocal
from app.models.candidate_profile import CandidateProfile

def check_db():
    db = SessionLocal()
    profiles = db.query(CandidateProfile).all()
    print(f"Found {len(profiles)} profiles.")
    for p in profiles:
        print(f"User ID: {p.user_id}")
        if p.profile_json:
            print("Keys in profile_json:", list(p.profile_json.keys()))
            print(json.dumps(p.profile_json, indent=2)[:500])
        else:
            print("profile_json is None or empty")
    db.close()

if __name__ == "__main__":
    check_db()
