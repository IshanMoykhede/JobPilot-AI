from uuid import UUID
from sqlalchemy.orm import Session
from app.models.candidate_profile import CandidateProfile

def check_profile_exists(db: Session, user_id: UUID) -> bool:
    """
    Check whether a CandidateProfile exists for a given user.
    """
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
    return profile is not None

def get_candidate_profile_by_user_id(db: Session, user_id: UUID) -> CandidateProfile:
    """
    Retrieve CandidateProfile for a given user.
    """
    return db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()

def create_candidate_profile(db: Session, user_id: UUID, profile_data: dict) -> CandidateProfile:
    """
    Create a new CandidateProfile for the user with profile_json.
    """
    db_profile = CandidateProfile(
        user_id=user_id,
        profile_json=profile_data,
        onboarding_completed=True
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

