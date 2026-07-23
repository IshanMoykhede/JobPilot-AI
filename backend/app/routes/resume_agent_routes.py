import logging
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.resume import Resume

from app.resume_tailoring_agent.services.resume_service import ResumeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/resume", tags=["Resume Agent"])

class GenerateResumeRequest(BaseModel):
    user_query: Optional[str] = None
    target_job_description: Optional[str] = None

class ContinueResumeRequest(BaseModel):
    message: str

@router.get("", summary="Get all generated resumes for the current user")
def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.updated_at.desc()).all()
    return [
        {
            "id": str(r.id),
            "title": r.title,
            "status": r.status,
            "created_at": r.created_at,
            "updated_at": r.updated_at
        }
        for r in resumes
    ]

@router.get("/{resume_id}", summary="Get the current state of a specific resume generation")
def get_resume_state(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ResumeService(db)
    try:
        state = service.get_resume_state(current_user.id, resume_id)
        if not state:
            raise HTTPException(status_code=404, detail="State not found in checkpointer")
        return state
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

class RenameResumeRequest(BaseModel):
    title: str

@router.patch("/{resume_id}/title", summary="Rename a specific resume")
def rename_resume(
    resume_id: UUID,
    request: RenameResumeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ResumeService(db)
    try:
        return service.rename_resume(current_user.id, resume_id, request.title)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.delete("/{resume_id}", summary="Delete a specific resume")
def delete_resume(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ResumeService(db)
    try:
        service.delete_resume(current_user.id, resume_id)
        return {"detail": "Resume deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/generate/stream", summary="Start generating a new resume")
def generate_resume_stream(
    req: GenerateResumeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.candidate_profile:
        raise HTTPException(status_code=400, detail="Candidate profile not found")
        
    service = ResumeService(db)
    
    return StreamingResponse(
        service.start_resume_generation(
            user=current_user,
            user_query=req.user_query,
            job_description=req.target_job_description or "General Software Engineering Role"
        ),
        media_type="text/event-stream"
    )

@router.post("/{resume_id}/continue/stream", summary="Continue an ongoing generation (HITL or Edit)")
def continue_resume_stream(
    resume_id: UUID,
    req: ContinueResumeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ResumeService(db)
    
    return StreamingResponse(
        service.continue_resume_generation(
            user_id=current_user.id,
            resume_id=resume_id,
            user_message=req.message
        ),
        media_type="text/event-stream"
    )

@router.post("/{resume_id}/retry/stream", summary="Retry an interrupted generation")
def retry_resume_stream(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ResumeService(db)
    
    return StreamingResponse(
        service.retry_resume_generation(
            user_id=current_user.id,
            resume_id=resume_id
        ),
        media_type="text/event-stream"
    )
