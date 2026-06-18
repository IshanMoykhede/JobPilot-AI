from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.services.profile_service import check_profile_exists, get_candidate_profile_by_user_id, create_candidate_profile

from app.schemas.candidate_profile import (
    ProfileStatusResponse,
    ParseResumeRequest,
    ParseResumeResponse,
    CompleteOnboardingRequest,
    CompleteOnboardingResponse,
    CandidateProfileResponse
)
from app.services.resume_parser import ResumeParserService

router = APIRouter(
    prefix="/profile",
    tags=["Candidate Profile"]
)

@router.get("/status", response_model=ProfileStatusResponse)
async def get_profile_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Determine whether a Candidate Profile exists.
    Frontend will use this immediately after login.
    
    NOTE: This endpoint requires an authenticated user.
    Will eventually use `Depends(get_current_user)` to fetch the user ID.
    """
    exists = check_profile_exists(db, current_user.id)
    return ProfileStatusResponse(profile_exists=exists)

@router.post("/parse-resume", response_model=ParseResumeResponse)
async def parse_resume(
    payload: ParseResumeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Accept parsed raw resume text from frontend.
    Call ResumeParserService to convert raw text into structured JSON.
    Return parsed structured candidate data.
    
    IMPORTANT: This endpoint must NOT save anything to the database.
    """
    try:
        parsed_data = ResumeParserService.parse_resume_text(payload.resume_text)
        return parsed_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error during resume parsing: {str(e)}")

@router.post("/complete-onboarding", response_model=CompleteOnboardingResponse)
async def complete_onboarding(
    payload: CompleteOnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Receive verified resume data, user preferences, and resume metadata.
    Persist Candidate Profile.
    Mark onboarding as completed.
    """
    # Store complete payload data in profile_json to satisfy Pydantic response models
    profile_data = payload.model_dump(mode="json")
    
    db_profile = get_candidate_profile_by_user_id(db, current_user.id)
    if db_profile:
        db_profile.profile_json = profile_data
        db_profile.onboarding_completed = True
        db.commit()
        db.refresh(db_profile)
        msg = "Profile updated successfully"
    else:
        db_profile = create_candidate_profile(db, current_user.id, profile_data)
        msg = "Profile created successfully"
    
    return CompleteOnboardingResponse(
        message=msg,
        profile_id=db_profile.id
    )

@router.get("/me", response_model=CandidateProfileResponse)
async def get_current_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Return the complete Candidate Profile for the authenticated user.
    This will later be used by the Dashboard, Profile Page, and Job Matching Engine.
    """
    profile = get_candidate_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    return profile

