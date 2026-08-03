import sys
sys.path.append('.')
from uuid import UUID

from app.core.database import SessionLocal
from app.models.candidate_profile import CandidateProfile  # FIX IMPORT ORDER
from app.models.user import User
from app.resume_tailoring_agent.services.resume_service import ResumeService

def test():
    db = SessionLocal()
    user = db.query(User).first()
    
    service = ResumeService(db)
    resume_id = UUID("a762af22-9e79-431b-9043-2f124e9b058b")
    
    print(f"Testing for user {user.id} and resume {resume_id}")
    try:
        resume = service.repository.get_resume(resume_id)
        if not resume:
            print("Resume not found in repository!")
        else:
            print(f"Resume user_id: {resume.user_id}")
            print(f"Matches user? {resume.user_id == user.id}")
            
        state = service.get_resume_state(user.id, resume_id)
        print("Success! State returned.")
        print(f"Keys: {state.keys()}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
    db.close()

if __name__ == "__main__":
    test()
