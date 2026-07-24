import sys
sys.path.append('.')
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_insights import CandidateInsights
from app.core.database import SessionLocal

def test():
    db = SessionLocal()
    try:
        profile = db.query(CandidateProfile).first()
        if not profile:
            print("No profile found.")
            return
            
        print("Profile User ID:", profile.user_id)
        
        # Get latest candidate insights
        insight = db.query(CandidateInsights).filter(
            CandidateInsights.candidate_profile_id == profile.id,
            CandidateInsights.artifact_type == 'CANDIDATE_KNOWLEDGE'
        ).order_by(CandidateInsights.created_at.desc()).first()
        
        if insight and insight.artifact_json:
            print("Candidate Insights Keys:", list(insight.artifact_json.keys()))
            for k in list(insight.artifact_json.keys()):
                val = insight.artifact_json[k]
                print(f"Key: {k}, type: {type(val)}")
                if isinstance(val, dict):
                    print(f"  Inner Keys: {list(val.keys())}")
                elif isinstance(val, list) and val:
                    print(f"  List length: {len(val)}, first item keys: {list(val[0].keys()) if isinstance(val[0], dict) else 'non-dict'}")
                    if isinstance(val[0], dict):
                        print(f"  First item content sample: {str(val[0])[:200]}")
        else:
            print("No insights found.")
    finally:
        db.close()

if __name__ == "__main__":
    test()
