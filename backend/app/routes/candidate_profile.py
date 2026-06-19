from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime, timezone
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
from app.services.evidence_engine import EvidenceEngineService
from app.graph.workflow import build_intelligence_graph
from app.graph.state import IntelligenceGraphState
from app.models.candidate_insights import CandidateInsights, InsightStatus

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

def calculate_profile_completeness(profile_json: dict) -> tuple[float, list[str]]:
    """
    Given a profile_json dictionary, calculate the completeness score (0 to 100)
    and return a list of missing fields.
    10 fields:
    1. contact_info.phone
    2. contact_info.linkedin_url
    3. contact_info.github_url
    4. contact_info.portfolio_url
    5. resume_data.summary
    6. resume_data.skills
    7. resume_data.experience
    8. resume_data.education
    9. resume_data.projects
    10. resume_data.certifications
    """
    resume_data = profile_json.get("resume_data", {}) or {}
    contact_info = resume_data.get("contact_info", {}) or {}
    
    fields_checked = [
        ("Phone Number", contact_info.get("phone")),
        ("LinkedIn URL", contact_info.get("linkedin_url")),
        ("GitHub URL", contact_info.get("github_url")),
        ("Portfolio URL", contact_info.get("portfolio_url")),
        ("Professional Summary", resume_data.get("summary")),
        ("Skills List", resume_data.get("skills")),
        ("Work Experience", resume_data.get("experience")),
        ("Education", resume_data.get("education")),
        ("Projects", resume_data.get("projects")),
        ("Certifications", resume_data.get("certifications"))
    ]
    
    filled_count = 0
    missing_fields = []
    
    for label, val in fields_checked:
        if val:
            if isinstance(val, list):
                if len(val) > 0:
                    filled_count += 1
                else:
                    missing_fields.append(label)
            elif isinstance(val, str) and val.strip():
                filled_count += 1
            else:
                missing_fields.append(label)
        else:
            missing_fields.append(label)
            
    percentage = (filled_count / len(fields_checked)) * 100.0
    return percentage, missing_fields

@router.get("/insights")
async def get_candidate_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get cached candidate insights and calculate profile completeness status (NO_INSIGHTS, STALE, COMPLETED).
    """
    profile = get_candidate_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")
        
    profile_json = profile.profile_json or {}
    
    # Calculate deterministic profile completeness
    completeness_score, missing_fields = calculate_profile_completeness(profile_json)
    
    # Retrieve the latest insights snapshot
    insight = db.query(CandidateInsights).filter(
        CandidateInsights.candidate_profile_id == profile.id
    ).order_by(CandidateInsights.created_at.desc()).first()
    
    if not insight or not insight.insights_json:
        return {
            "status": "NO_INSIGHTS",
            "profile_completeness": completeness_score,
            "missing_fields": missing_fields,
            "insights": None,
            "generated_at": None
        }
        
    # Check if the cached insights are stale based on profile update time
    profile_updated = profile.updated_at
    insight_generated = insight.generated_at
    
    # Timezone normalization
    if profile_updated and profile_updated.tzinfo is None:
        profile_updated = profile_updated.replace(tzinfo=timezone.utc)
    if insight_generated and insight_generated.tzinfo is None:
        insight_generated = insight_generated.replace(tzinfo=timezone.utc)
        
    status = "COMPLETED"
    if profile_updated and insight_generated and profile_updated > insight_generated:
        status = "STALE"
        
    return {
        "status": status,
        "profile_completeness": completeness_score,
        "missing_fields": missing_fields,
        "insights": insight.insights_json,
        "generated_at": insight.generated_at
    }

@router.post("/insights/generate")
async def generate_candidate_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Force run the Evidence Engine and execute the LangGraph workflow asynchronously.
    Updates or inserts the snapshot in CandidateInsights database table.
    """
    profile = get_candidate_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found. Please complete onboarding first.")
        
    profile_json = profile.profile_json
    if not profile_json:
        raise HTTPException(status_code=400, detail="Profile details are empty.")
        
    # Calculate completeness
    completeness_score, missing_fields = calculate_profile_completeness(profile_json)
    
    # Parse profile for evidence engine
    try:
        profile_req = CompleteOnboardingRequest(**profile_json)
    except Exception as parse_err:
        raise HTTPException(status_code=400, detail=f"Invalid profile format in database: {parse_err}")
        
    # Run Evidence Engine
    evidence = EvidenceEngineService.build_candidate_evidence(profile_req)
    
    # Run Async LangGraph Workflow
    state = IntelligenceGraphState(
        evidence=evidence,
        market_intelligence=None,
        market_intelligence_generated_at=None,
        recommendations=None,
        recommendations_generated_at=None
    )
    
    graph = build_intelligence_graph()
    config = {"configurable": {"db": db}}
    
    try:
        final_state = await graph.ainvoke(state, config=config)
    except Exception as graph_err:
        raise HTTPException(status_code=500, detail=f"Failed to execute career intelligence graph: {str(graph_err)}")

    # --- Build the complete insights payload ---
    market_intel_dump = {}
    if final_state.get("market_intelligence"):
        for role, intel in final_state["market_intelligence"].items():
            market_intel_dump[role] = intel.model_dump(mode="json")

    recommendations_dump = {}
    if final_state.get("recommendations"):
        for role, res in final_state["recommendations"].items():
            recommendations_dump[role] = res.model_dump(mode="json")

    full_insights_json = {
        "evidence_engine": evidence.model_dump(mode="json"),
        "market_intelligence": market_intel_dump,
        "recommendations": recommendations_dump
    }

    # --- Upsert: update existing latest insight row, or create a new one ---
    generated_now = datetime.now(timezone.utc)

    existing_insight = db.query(CandidateInsights).filter(
        CandidateInsights.candidate_profile_id == profile.id
    ).order_by(CandidateInsights.created_at.desc()).first()

    if existing_insight:
        existing_insight.insights_json = full_insights_json
        existing_insight.status = InsightStatus.COMPLETED
        existing_insight.generated_at = generated_now
        flag_modified(existing_insight, "insights_json")
        insight = existing_insight
    else:
        insight = CandidateInsights(
            candidate_profile_id=profile.id,
            insights_json=full_insights_json,
            status=InsightStatus.COMPLETED,
            generated_at=generated_now
        )
        db.add(insight)

    db.commit()
    db.refresh(insight)

    return {
        "status": "COMPLETED",
        "profile_completeness": completeness_score,
        "missing_fields": missing_fields,
        "insights": full_insights_json,
        "generated_at": insight.generated_at
    }


