import uuid
import logging
import json
from typing import List
from datetime import datetime, timezone

from app.resume_tailoring_agent.state import ResumeAgentState
from app.resume_tailoring_agent.schemas.messaging import ResumeMessage, MessageRole, MessageType, MessageSource
from app.resume_tailoring_agent.schemas.common import ResumeSectionType, ResumeContent, ResumeSection, ResumeSectionState
from app.resume_tailoring_agent.schemas.co_curricular import CoCurricularGenerationResponse, CoCurricularActivity

from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import get_structured_llm

logger = logging.getLogger(__name__)

CO_CURRICULAR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert ATS-optimized resume writer.
Your task is to generate or modify the Co-Curricular Activities section of the resume.

CRITICAL INSTRUCTIONS:
1. ALWAYS, ALWAYS ADD EXACTLY WHAT THE USER REQUESTS in the "User Request" field. Do NOT evaluate its relevance to the job. If the user wants to add a sport, hobby, or anything else, YOU MUST INCLUDE IT IN THE OUTPUT.
2. Keep all existing activities that are relevant to the target job description.
3. Combine the user's requested additions with the existing activities into the final JSON output.
4. Output must exactly match the required JSON schema.
"""),
    ("user", """
Target Job Information:
{job_info}

Existing Co-Curricular Activities (if any):
{existing_activities}

User Request (What you need to do):
{user_request}
""")
])

from .utils import safe_state_node

@safe_state_node
def co_curricular_generator_node(state: ResumeAgentState) -> ResumeAgentState:
    """Workflow node responsible for generating the Co-Curricular Activities section."""
    
    # Step 1 – Validate Invocation
    if not state.messages:
        return state
        
    latest_msg = state.messages[-1]
    
    # Only process if routed here via a WORKFLOW_REQUEST
    if latest_msg.message_type != MessageType.WORKFLOW_REQUEST or latest_msg.to_node != MessageSource.CO_CURRICULAR_GENERATOR:
        return state

    logger.info(f"[Co-Curricular Workflow] Starting generation for resume {state.resume_id}")

    # Step 2 – Check for skip/remove intents directly in the user request
    user_msg = latest_msg.content.lower() if latest_msg.content else ""
    if user_msg and (any(w in user_msg for w in ["remove all", "delete all", "clear all", "skip", "ignore", "don't have", "none"]) or user_msg in ["remove", "delete", "clear"]):
        logger.info("[Co-Curricular Workflow] User requested to remove/skip section.")
        if not state.resume_content:
            state.resume_content = ResumeContent(sections=[])
        state.resume_content.sections = [s for s in state.resume_content.sections if s.section_type != ResumeSectionType.CO_CURRICULAR]
        
        skip_msg = ResumeMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            role=MessageRole.ASSISTANT,
            message_type=MessageType.WORKFLOW_RESPONSE,
            from_node=MessageSource.CO_CURRICULAR_GENERATOR,
            to_node=MessageSource.INTENT_ROUTER,
            related_section=ResumeSectionType.CO_CURRICULAR,
            content="I have removed the Co-Curricular Activities section as requested.",
            payload={"status": "COMPLETED"}
        )
        state.messages.append(skip_msg)
        return state

    # Step 3 – Prepare LLM Inputs
    job_info = state.job_knowledge or "General Professional Role"

    existing_activities = "None"
    if state.resume_content:
        for section in state.resume_content.sections:
            if section.section_type == ResumeSectionType.CO_CURRICULAR:
                existing_activities = json.dumps([act if isinstance(act, dict) else act.model_dump() for act in section.content], indent=2)
                break

    # Step 4 – Invoke LLM
    try:
        llm = get_structured_llm(CoCurricularGenerationResponse)
        chain = CO_CURRICULAR_PROMPT | llm
        
        logger.info("[Co-Curricular Workflow] Invoking LLM...")
        output: CoCurricularGenerationResponse = chain.invoke({
            "job_info": job_info,
            "existing_activities": existing_activities,
            "user_request": latest_msg.content
        })
        logger.info("[Co-Curricular Workflow] LLM generation successful.")
        
    except Exception as e:
        logger.error(f"[Co-Curricular Workflow] Generation failed: {e}")
        error_msg = ResumeMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            role=MessageRole.SYSTEM,
            message_type=MessageType.WORKFLOW_RESPONSE,
            from_node=MessageSource.CO_CURRICULAR_GENERATOR,
            to_node=MessageSource.INTENT_ROUTER,
            related_section=ResumeSectionType.CO_CURRICULAR,
            content=f"Co-Curricular generation failed: {e}",
            payload={"status": "FAILED"}
        )
        state.messages.append(error_msg)
        return state

    # Step 5 – Update Resume
    if not state.resume_content:
        state.resume_content = ResumeContent(sections=[])
        
    new_section = ResumeSection(
        section_type=ResumeSectionType.CO_CURRICULAR,
        display_name="Co-Curricular Activities",
        status=ResumeSectionState.COMPLETED,
        content=output.activities
    )
    
    # Remove old section and append new
    state.resume_content.sections = [s for s in state.resume_content.sections if s.section_type != ResumeSectionType.CO_CURRICULAR]
    if output.activities:
        state.resume_content.sections.append(new_section)

    # Step 6 – Notify Completion
    completion_msg = ResumeMessage(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        role=MessageRole.ASSISTANT,
        message_type=MessageType.WORKFLOW_RESPONSE,
        from_node=MessageSource.CO_CURRICULAR_GENERATOR,
        to_node=MessageSource.INTENT_ROUTER,
        related_section=ResumeSectionType.CO_CURRICULAR,
        content=output.user_update_message,
        payload={"status": "COMPLETED"}
    )
    state.messages.append(completion_msg)

    return state
