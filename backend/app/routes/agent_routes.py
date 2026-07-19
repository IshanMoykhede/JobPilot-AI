import logging
from typing import Optional, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.agent.services.orchestration_service import OrchestrationService
from app.dependencies.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["Agent"])

class AgentChatRequest(BaseModel):
    message: str = Field(..., description="The natural language query or message from the user.")
    conversation_id: Optional[UUID] = Field(None, description="Optional conversation ID if continuing an existing thread.")

@router.post("/chat", summary="Single AI entry point for the frontend.")
async def chat_with_agent(
    request: AgentChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Routes a user request through the LangGraph Orchestrator.
    Determines intent and delegates to the appropriate agent pipeline (e.g. Job Search).
    """
    if not current_user.candidate_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must complete onboarding to create a candidate profile before using the agent."
        )
        
    candidate_profile_id = current_user.candidate_profile.id
    logger.info(f"POST /agent/chat - user={current_user.id} candidate={candidate_profile_id}")
    
    try:
        final_state = await OrchestrationService.run_graph(
            db=db,
            candidate_profile_id=candidate_profile_id,
            user_id=current_user.id,
            user_query=request.message,
            conversation_id=request.conversation_id
        )
        # If the graph executed a job search, build the rich API payload
        workspace_id = final_state.get("workspace_id")
        if workspace_id:
            from app.presentation.job_search_response_assembler import JobSearchResponseAssembler
            response_dto = JobSearchResponseAssembler.build_response(
                db=db,
                workspace_id=workspace_id,
            )
            return response_dto.model_dump()
            
        # Otherwise return the standard conversational response
        return final_state.get("response")
    except Exception as e:
        logger.error(f"Error in /agent/chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during agent orchestration: {str(e)}"
        )
from app.conversation.models.conversation import Conversation
from app.conversation.models.conversation_message import ConversationMessage

@router.get("/conversations", summary="List all conversations for the user.")
async def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    if not current_user.candidate_profile:
        return []
    
    conversations = db.query(Conversation).filter(
        Conversation.candidate_profile_id == current_user.candidate_profile.id
    ).order_by(Conversation.updated_at.desc()).all()
    
    return [
        {
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at,
            "updated_at": c.updated_at
        } for c in conversations
    ]

@router.get("/conversations/{conversation_id}", summary="Get messages for a specific conversation.")
async def get_conversation_messages(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    if not current_user.candidate_profile:
        raise HTTPException(status_code=400, detail="No candidate profile found.")
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.candidate_profile_id == current_user.candidate_profile.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    messages_out = []
    for m in conversation.messages:
        content = m.content or {}
        role = m.role.value if hasattr(m.role, 'value') else m.role
        msg_type = m.message_type.value if hasattr(m.message_type, 'value') else m.message_type
        
        # If this is a JOB_RESULTS message and there is an active workspace, reconstruct the payload
        if msg_type == "JOB_RESULTS" and conversation.active_workspace_id:
            try:
                from app.presentation.job_search_response_assembler import JobSearchResponseAssembler
                
                exps = []
                is_explanations_msg = isinstance(content, dict) and content.get("type") == "job_explanations"
                
                if is_explanations_msg:
                    from app.explanation.schemas.explanation import JobExplanation
                    exps = [JobExplanation(**exp) for exp in content.get("explanations", [])]
                
                # Only inject payload if it's the explanations message (which has the rich data)
                # OR if it's the final orchestration message but there were NO explanations generated at all.
                # To simplify, we inject it ONLY if it's the explanations message. 
                # If there are no explanations, the job search basically failed to generate insights, 
                # but we can fallback to injecting into any JOB_RESULTS if we must. 
                if is_explanations_msg:
                    response_dto = JobSearchResponseAssembler.build_response(
                        db=db,
                        workspace_id=conversation.active_workspace_id
                    )
                    
                    if isinstance(content, dict):
                        content = dict(content)
                    else:
                        content = {"original_content": content}
                        
                    content["payload"] = response_dto.payload.model_dump()
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Failed to rebuild payload for conversation {conversation_id}: {e}")

        messages_out.append({
            "id": m.id,
            "role": role.lower() if isinstance(role, str) else role,
            "content": content,
            "created_at": m.created_at
        })
        
    return messages_out

@router.delete("/conversations/{conversation_id}", summary="Delete a specific conversation.")
async def delete_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    if not current_user.candidate_profile:
        raise HTTPException(status_code=400, detail="No candidate profile found.")
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.candidate_profile_id == current_user.candidate_profile.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    db.delete(conversation)
    db.commit()
    return {"status": "SUCCESS", "message": "Conversation deleted successfully."}


@router.get("/test-serp", summary="Directly test the SerpService and QueryParser.")
async def test_serp(
    query: str,
    location: Optional[str] = None
) -> Any:
    from app.job_search.services.serp_service import SerpService
    from app.job_search.services.query_parser_service import QueryParserService
    
    try:
        # Parse the query first
        parsed = QueryParserService.parse(query)
        final_location = parsed.location if parsed.location else location

        # Fetch jobs using the parsed role and location
        service = SerpService()
        raw_jobs = service.search_jobs(query=parsed.role, location=final_location)
        
        return {
            "status": "SUCCESS", 
            "original_query": query, 
            "parsed_role": parsed.role,
            "parsed_location": parsed.location,
            "serp_params": {
                "q": parsed.role,
                "location": final_location
            },
            "jobs_count": len(raw_jobs),
            "jobs": raw_jobs
        }
    except Exception as e:
        logger.error(f"Error in /agent/test-serp: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
