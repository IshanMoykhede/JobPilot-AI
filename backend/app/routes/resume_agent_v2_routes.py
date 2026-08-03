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

class StartTailoringRequest(BaseModel):
    title: Optional[str] = "Tailored Resume"
    target_job_description: Optional[str] = None

class ChatRequest(BaseModel):
    message: str

@router.post("/start", summary="Initialize a new V2 Resume Tailoring Session")
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
    # Fetch Candidate Insights
    profile_id = current_user.candidate_profile.id if current_user.candidate_profile else None
    insights = None
    if profile_id:
        insights = db.query(CandidateInsights).filter(CandidateInsights.candidate_profile_id == profile_id).first()
    user_knowledge = insights.artifact_json if insights and insights.artifact_json else {}
    
    # Construct JobKnowledge from the provided description
    job_knowledge = {
        "title": "Target Role",
        "description": req.target_job_description or "General Software Engineering Role"
    }
    
    initial_state = ResumeTailoringState(
        session_id=str(new_resume.id),
        job_knowledge=job_knowledge,
        user_knowledge=user_knowledge,
        pending_sections=["summary", "experience", "education", "skills", "projects", "certifications"],
        messages=[],
        drafts={}
    )
    
    # 3. Save initial state to Checkpointer (so it's ready for the first chat)
    checkpointer = get_checkpointer()
    agent_app = build_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": str(new_resume.id)}}
    agent_app.update_state(config, initial_state.model_dump())
    
    return {"resume_id": str(new_resume.id)}

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
