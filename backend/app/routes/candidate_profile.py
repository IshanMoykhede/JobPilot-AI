from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
import logging
import json
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime, timezone
from app.core.database import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.services.profile_service import check_profile_exists, get_candidate_profile_by_user_id, create_candidate_profile

logger = logging.getLogger(__name__)

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
from app.services.knowledge_engine import CandidateKnowledgeEngine
from app.services.project_intelligence import ProjectIntelligenceService
from app.services.experience_intelligence import ExperienceIntelligenceService
from app.services.academic_intelligence import AcademicIntelligenceService
from app.services.knowledge_fusion import KnowledgeFusionService
from app.services.evidence_engine_v2 import EvidenceEngineV2
from app.core.evaluation_strategy import DefaultEvaluationStrategy
from app.services.candidate_synthesizer import CandidateSynthesizerService
from app.schemas.evidence import CandidateSynthesisInput, CandidateKnowledge
from app.models.candidate_insights import CandidateInsights, InsightStatus, ArtifactType
from app.graph.workflow import build_intelligence_graph
from app.graph.state import IntelligenceGraphState

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
        parsed_data = await ResumeParserService.parse_resume_text(payload.resume_text)
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
    Runs inside a single atomic database transaction. If any part (including LLM extraction)
    fails, the entire operation is rolled back.
    """
    try:
        profile_data = payload.model_dump(mode="json")
        
        db_profile = get_candidate_profile_by_user_id(db, current_user.id)
        if db_profile:
            db_profile.profile_json = profile_data
            db_profile.onboarding_completed = True
            db.flush()
            db.refresh(db_profile)
            msg = "Profile updated successfully"
        else:
            db_profile = create_candidate_profile(db, current_user.id, profile_data)
            msg = "Profile created successfully"
            
        # Mark knowledge as STALE and then regenerate it
        CandidateKnowledgeEngine.mark_knowledge_stale(db, db_profile)
        await CandidateKnowledgeEngine.generate_and_persist(db, db_profile)
        
        # Commit the transaction ONLY after everything succeeds
        db.commit()
        db.refresh(db_profile)
        
        return CompleteOnboardingResponse(
            message=msg,
            profile_id=db_profile.id
        )
    except Exception as e:
        db.rollback()
        logger.exception(e)
        logger.error(f"Onboarding failed. Database transaction rolled back. Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Candidate onboarding failed and was rolled back. Details: {str(e)}"
        )

@router.post("/complete-onboarding-stream")
async def complete_onboarding_stream(
    payload: CompleteOnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Onboard user and stream the real progress of the Candidate Knowledge Engine.
    Runs inside a single atomic database transaction. If any part fails, it rolls back.
    """
    async def event_generator():
        try:
            # 1. Start Transaction & Parse Profile
            yield f"data: {json.dumps({'status': 'processing', 'stage': 'parsing', 'message': 'Parsing resume structure & properties'})}\n\n"
            await asyncio.sleep(0.5)
            
            profile_data = payload.model_dump(mode="json")
            db_profile = get_candidate_profile_by_user_id(db, current_user.id)
            if db_profile:
                db_profile.profile_json = profile_data
                db_profile.onboarding_completed = True
                db.flush()
                db.refresh(db_profile)
            else:
                db_profile = create_candidate_profile(db, current_user.id, profile_data)
            
            # 2. Extracting Intelligence Agents (Projects, Experience, Academics)
            yield f"data: {json.dumps({'status': 'processing', 'stage': 'intelligence', 'message': 'Running concurrent Intelligence Agents (Projects, Experience, Academics)'})}\n\n"
            
            projects = payload.resume_data.projects
            experience = payload.resume_data.experience
            education = payload.resume_data.education
            certifications = payload.resume_data.certifications
            
            project_intel, exp_intel, edu_intel, cert_intel = await asyncio.gather(
                ProjectIntelligenceService.analyze_projects(projects),
                ExperienceIntelligenceService.analyze_experiences(experience),
                AcademicIntelligenceService.analyze_education(education),
                AcademicIntelligenceService.analyze_certifications(certifications)
            )
            
            # 3. Knowledge Fusion
            yield f"data: {json.dumps({'status': 'processing', 'stage': 'fusion', 'message': 'Fusing extracted intelligence into Unified Knowledge profile'})}\n\n"
            
            unified_knowledge = await KnowledgeFusionService.fuse_knowledge(
                skills=payload.resume_data.skills,
                project_intel=project_intel,
                exp_intel=exp_intel,
                edu_intel=edu_intel,
                cert_intel=cert_intel
            )
            
            # 4. Evidence Evaluation (V2)
            yield f"data: {json.dumps({'status': 'processing', 'stage': 'evidence', 'message': 'Running Evidence Engine V2 competency checks'})}\n\n"
            
            strategy = DefaultEvaluationStrategy()
            evidence_report = EvidenceEngineV2.evaluate(unified_knowledge, strategy)
            evidence = EvidenceEngineService.build_candidate_evidence(payload, project_intel)
            
            # 5. Candidate Synthesis (LLM)
            yield f"data: {json.dumps({'status': 'processing', 'stage': 'synthesis', 'message': 'Synthesizing final Candidate Engineering Identity'})}\n\n"
            
            synthesis_input = CandidateSynthesisInput(
                unified_knowledge=unified_knowledge,
                evidence_report=evidence_report,
                project_intelligence=project_intel,
                experience_intelligence=exp_intel,
                education_intelligence=edu_intel,
                certification_intelligence=cert_intel
            )
            synthesizer = CandidateSynthesizerService()
            candidate_identity = await synthesizer.synthesize(synthesis_input)
            
            # 6. Assembly & DB Persistence
            yield f"data: {json.dumps({'status': 'processing', 'stage': 'persistence', 'message': 'Finalizing database transaction & committing insights'})}\n\n"
            
            candidate_knowledge = CandidateKnowledge(
                candidate_level=evidence.candidate_level,
                candidate_maturity=evidence.candidate_maturity,
                unified_knowledge=unified_knowledge,
                evidence_report=evidence_report,
                candidate_identity=candidate_identity,
                project_intelligence=project_intel,
                experience_intelligence=exp_intel,
                education_intelligence=edu_intel,
                certification_intelligence=cert_intel
            )
            artifact_data = candidate_knowledge.model_dump(mode="json")
            generated_now = datetime.now(timezone.utc)
            
            # Upsert insight
            insight = db.query(CandidateInsights).filter(
                CandidateInsights.candidate_profile_id == db_profile.id,
                CandidateInsights.artifact_type == ArtifactType.CANDIDATE_KNOWLEDGE
            ).order_by(CandidateInsights.created_at.desc()).first()

            if insight:
                insight.artifact_json = artifact_data
                insight.status = InsightStatus.COMPLETED
                insight.generated_at = generated_now
                flag_modified(insight, "artifact_json")
            else:
                insight = CandidateInsights(
                    candidate_profile_id=db_profile.id,
                    artifact_type=ArtifactType.CANDIDATE_KNOWLEDGE,
                    artifact_json=artifact_data,
                    status=InsightStatus.COMPLETED,
                    generated_at=generated_now
                )
                db.add(insight)
            
            db.flush()
            db.commit()
            
            yield f"data: {json.dumps({'status': 'success', 'profile_id': str(db_profile.id), 'message': 'Onboarding completed successfully!'})}\n\n"
            
        except Exception as e:
            db.rollback()
            logger.exception(e)
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

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

from app.services.knowledge_engine import CandidateKnowledgeEngine

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
    
    # Retrieve the latest CANDIDATE_KNOWLEDGE snapshot
    insight = db.query(CandidateInsights).filter(
        CandidateInsights.candidate_profile_id == profile.id,
        CandidateInsights.artifact_type == ArtifactType.CANDIDATE_KNOWLEDGE
    ).order_by(CandidateInsights.created_at.desc()).first()
    
    if not insight or not insight.artifact_json:
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
        
    from typing import cast
    from app.schemas.evidence import CandidateKnowledge
    ck = CandidateKnowledge(**(cast(dict, insight.artifact_json) or {}))
        
    return {
        "status": status,
        "profile_completeness": completeness_score,
        "missing_fields": missing_fields,
        "insights": {
            "evidence_engine": ck.model_dump(mode="json"),
            "project_intelligence": [p.model_dump(mode="json") for p in ck.project_intelligence]
        },
        "generated_at": insight.generated_at
    }

@router.post("/insights/generate")
async def generate_candidate_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Force run the Candidate Knowledge Engine (if needed) and execute the LangGraph workflow asynchronously.
    """
    profile = get_candidate_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found. Please complete onboarding first.")
        
    profile_json = profile.profile_json
    if not profile_json:
        raise HTTPException(status_code=400, detail="Profile details are empty.")
        
    # Calculate completeness
    completeness_score, missing_fields = calculate_profile_completeness(profile_json)
    
    # Self-healing regeneration of Candidate Knowledge
    try:
        knowledge = await CandidateKnowledgeEngine.ensure_candidate_knowledge(db, profile)
        
        # TODO(Sprint 2/3): The graph should eventually consume CandidateKnowledge directly.
        # Rebuilding CandidateEvidence here is a temporary compatibility bridge for Sprint 1.
        from typing import cast
        from app.schemas.evidence import CandidateKnowledge, CandidateEvidence, EvidenceSummary, SkillEvidenceItem
        ck = CandidateKnowledge(**(cast(dict, knowledge.artifact_json) or {}))
        
        skill_evidence_map = {}
        if hasattr(ck, "evidence_report") and ck.evidence_report and ck.evidence_report.evaluations:
            for skill, eval_item in ck.evidence_report.evaluations.items():
                tier = "Demonstrated" if eval_item.practical_demonstration > 50 else "Claimed"
                skill_evidence_map[skill] = SkillEvidenceItem(
                    total_score=eval_item.confidence_score,
                    tier=tier,
                    sources=[]
                )
                
        evidence = CandidateEvidence(
            candidate_level=ck.candidate_level,
            candidate_maturity=ck.candidate_maturity,
            current_domains=[d.value for d in ck.candidate_identity.engineering_domains] if ck.candidate_identity else [],
            target_domains=[ck.candidate_identity.primary_specialization] + ck.candidate_identity.secondary_specializations if ck.candidate_identity else ["General Software Engineer"],
            skill_evidence=skill_evidence_map,
            evidence_summary=EvidenceSummary(
                total_skills_detected=len(skill_evidence_map),
                demonstrated_skills_count=len([s for s in skill_evidence_map.values() if s.tier == "Demonstrated"]),
                claimed_only_skills_count=len([s for s in skill_evidence_map.values() if s.tier == "Claimed"])
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load or generate Candidate Knowledge: {str(e)}")
    
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
        "evidence_engine": ck.model_dump(mode="json"),
        "project_intelligence": [p.model_dump(mode="json") for p in ck.project_intelligence],
        "market_intelligence": market_intel_dump,
        "recommendations": recommendations_dump
    }

    # Fetch the generated_at from the knowledge artifact to return
    insight = db.query(CandidateInsights).filter(
        CandidateInsights.candidate_profile_id == profile.id,
        CandidateInsights.artifact_type == ArtifactType.CANDIDATE_KNOWLEDGE
    ).order_by(CandidateInsights.created_at.desc()).first()

    return {
        "status": "COMPLETED",
        "profile_completeness": completeness_score,
        "missing_fields": missing_fields,
        "insights": full_insights_json,
        "generated_at": insight.generated_at if insight else datetime.now(timezone.utc)
    }


