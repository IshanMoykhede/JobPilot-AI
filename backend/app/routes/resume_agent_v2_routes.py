import logging
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from langchain_core.runnables import RunnableConfig

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.resume import Resume, ResumeContentModel, ResumeMessageModel
from app.models.candidate_insights import CandidateInsights

from app.resume_tailoring_agent_v2.graph import build_graph
from app.resume_tailoring_agent_v2.state import ResumeTailoringState
from app.resume_tailoring_agent_v2.checkpointer import get_checkpointer
from app.resume_tailoring_agent_v2.schemas.messaging import MessageRole, MessageType, MessageSource, ResumeSectionType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/resume", tags=["Resume Agent V2"])

import uuid
from app.job_search_agent.models.job_knowledge import JobKnowledge

class StartTailoringRequest(BaseModel):
    title: Optional[str] = "Tailored Resume"
    job_id: Optional[uuid.UUID] = None
    message: Optional[str] = "Draft my resume based on this job description."

class ChatRequest(BaseModel):
    message: str

@router.post("/start", summary="Initialize a new V2 Resume Tailoring Session and generate first section")
def start_session(
    req: StartTailoringRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Create Business Models
    new_resume = Resume(
        user_id=current_user.id,
        title=req.title,
        status="DRAFT"
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    
    new_content = ResumeContentModel(
        resume_id=new_resume.id,
        data={}
    )
    db.add(new_content)
    db.commit()
    
    # 2. Setup Initial LangGraph State
    profile_id = current_user.candidate_profile.id if current_user.candidate_profile else None
    insights = None
    if profile_id:
        insights = db.query(CandidateInsights).filter(CandidateInsights.candidate_profile_id == profile_id).first()
    user_knowledge = insights.artifact_json if insights and insights.artifact_json else {}
    
    job_knowledge = {}
    if req.job_id:
        job = db.query(JobKnowledge).filter(JobKnowledge.id == req.job_id).first()
        if job and job.raw_knowledge:
            job_knowledge = job.raw_knowledge
        elif job:
            job_knowledge = {
                "title": job.title,
                "description": job.capabilities if job.capabilities else ""
            }
    
    if not job_knowledge:
        job_knowledge = {
            "title": "Target Role",
            "description": "General Software Engineering Role"
        }
    
    initial_state = ResumeTailoringState(
        session_id=str(new_resume.id),
        job_knowledge=job_knowledge,
        user_knowledge=user_knowledge,
        pending_sections=["summary", "experience", "education", "skills", "projects", "certifications"],
        messages=[],
        drafts={}
    )
    
    # 3. Setup Checkpointer and Graph
    checkpointer = get_checkpointer()
    agent_app = build_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": str(new_resume.id)}}
    
    # Initialize state in checkpointer
    agent_app.update_state(config, initial_state.model_dump())
    
    # 4. Save Dummy User Message to DB
    user_msg = ResumeMessageModel(
        id=str(uuid.uuid4()),
        resume_id=new_resume.id,
        role=MessageRole.USER,
        message_type=MessageType.USER_QUERY,
        from_node=MessageSource.USER,
        to_node=MessageSource.SYSTEM,
        content=req.message
    )
    db.add(user_msg)
    db.commit()

    # 5. Invoke Graph with the Dummy Message
    logger.info(f"Invoking V2 Graph (Initial Run) for resume {new_resume.id}...")
    input_state = {"messages": [{"role": "user", "content": req.message}]}
    final_state = agent_app.invoke(input_state, config)
    
    # 6. Sync outputs back to business DB
    new_drafts = final_state.get("drafts", {})
    messages = final_state.get("messages", [])
    
    new_content.data = new_drafts
    db.commit()
        
    ai_response = "I have started drafting your resume."
    if messages and messages[-1].get("role") == "assistant":
        ai_response = messages[-1].get("content")
        
    ai_msg = ResumeMessageModel(
        id=str(uuid.uuid4()),
        resume_id=new_resume.id,
        role=MessageRole.ASSISTANT,
        message_type=MessageType.WORKFLOW_RESPONSE,
        from_node=MessageSource.SYSTEM,
        to_node=MessageSource.USER,
        content=ai_response
    )
    db.add(ai_msg)
    db.commit()
    
    # Format messages for frontend
    formatted_messages = [
        {"role": "USER", "content": req.message},
        {"role": "ASSISTANT", "content": ai_response}
    ]
    
    return {
        "resume_id": str(new_resume.id),
        "drafts": new_drafts,
        "messages": formatted_messages,
        "pending_sections": final_state.get("pending_sections", [])
    }

@router.post("/{resume_id}/chat", summary="Send a message to the V2 Agent")
def chat_with_agent(
    resume_id: uuid.UUID,
    req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify ownership
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    # Build graph with PostgresSaver
    checkpointer = get_checkpointer()
    agent_app = build_graph(checkpointer=checkpointer)
    
    config = {"configurable": {"thread_id": str(resume_id)}}
    
    # 1. Save user message to business table
    user_msg = ResumeMessageModel(
        id=str(uuid.uuid4()),
        resume_id=resume_id,
        role=MessageRole.USER,
        message_type=MessageType.USER_QUERY,
        from_node=MessageSource.USER,
        to_node=MessageSource.SYSTEM,
        content=req.message
    )
    db.add(user_msg)
    db.commit()
    
    # 2. Invoke Graph
    input_state = {"messages": [{"role": "user", "content": req.message}]}
    
    logger.info(f"Invoking V2 Graph for resume {resume_id}...")
    final_state = agent_app.invoke(input_state, config)
    
    # 3. Sync outputs back to business DB
    new_drafts = final_state.get("drafts", {})
    messages = final_state.get("messages", [])
    
    # Update ResumeContentModel
    content_record = db.query(ResumeContentModel).filter(ResumeContentModel.resume_id == resume_id).first()
    if content_record:
        content_record.data = new_drafts
        db.commit()
        
    # Extract the last AI message
    ai_response = "I have updated your resume."
    if messages and messages[-1].get("role") == "assistant":
        ai_response = messages[-1].get("content")
        
    ai_msg = ResumeMessageModel(
        id=str(uuid.uuid4()),
        resume_id=resume_id,
        role=MessageRole.ASSISTANT,
        message_type=MessageType.WORKFLOW_RESPONSE,
        from_node=MessageSource.SYSTEM,
        to_node=MessageSource.USER,
        content=ai_response
    )
    db.add(ai_msg)
    db.commit()
    
    # If pending_sections is empty, mark Resume as COMPLETED
    if not final_state.get("pending_sections"):
        resume.status = "COMPLETED"
        db.commit()
    
    return {
        "reply": ai_response,
        "drafts": new_drafts,
        "pending_sections": final_state.get("pending_sections", [])
    }

@router.get("/{resume_id}", summary="Get the complete state, drafts, and chat history of a V2 resume")
def get_resume(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch Resume
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    # Fetch Drafts
    content = db.query(ResumeContentModel).filter(ResumeContentModel.resume_id == resume_id).first()
    drafts = content.data if content else {}
    
    # Fetch Chat History
    messages = db.query(ResumeMessageModel).filter(ResumeMessageModel.resume_id == resume_id).order_by(ResumeMessageModel.created_at.asc()).all()
    formatted_messages = [
        {
            "id": msg.id,
            "role": msg.role.value,
            "content": msg.content,
            "created_at": msg.created_at
        }
        for msg in messages
    ]
    
    # Fetch pending_sections from LangGraph State
    checkpointer = get_checkpointer()
    config = {"configurable": {"thread_id": str(resume_id)}}
    checkpoint_tuple = checkpointer.get_tuple(config)
    pending_sections = []
    
    if checkpoint_tuple and checkpoint_tuple.checkpoint:
        # The state is stored inside the checkpoint dict depending on LangGraph version
        # It's usually inside 'channel_values' or 'values'
        state_values = checkpoint_tuple.checkpoint.get("channel_values", {})
        if not state_values:
            state_values = checkpoint_tuple.checkpoint.get("values", {})
            
        pending_sections = state_values.get("pending_sections", [])
        
    return {
        "id": str(resume.id),
        "title": resume.title,
        "status": resume.status,
        "drafts": drafts,
        "messages": formatted_messages,
        "pending_sections": pending_sections
    }

@router.get("/", summary="Get all V2 resumes for the current user")
def get_all_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()
    
    result = []
    for r in resumes:
        result.append({
            "id": str(r.id),
            "title": r.title,
            "status": r.status,
            "created_at": r.created_at
        })
        
    return result

@router.delete("/{resume_id}", summary="Delete a V2 resume and all its data")
def delete_resume(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    db.delete(resume)
    db.commit()
    
    return {"message": "Resume deleted successfully"}
