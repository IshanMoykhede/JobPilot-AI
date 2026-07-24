import uuid
import logging
import json
from typing import List
from datetime import datetime, timezone
from pydantic import BaseModel

from app.resume_tailoring_agent.state import ResumeAgentState
from app.resume_tailoring_agent.schemas.messaging import ResumeMessage, MessageRole, MessageType, MessageSource
from app.resume_tailoring_agent.schemas.common import ResumeSectionType, ResumeContent, ResumeSection, ResumeSectionState
from app.resume_tailoring_agent.schemas.certifications import CertificationEntry, CertificationsGenerationResponse

from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import get_structured_llm

logger = logging.getLogger(__name__)

CERTIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert ATS-optimized resume writer.
Your task is to generate or modify the Certifications section of the resume.

CRITICAL INSTRUCTIONS:
1. HONOR USER REQUESTS FIRST: If the "User Request" asks to add, remove, or modify a specific item (e.g., adding a certification), YOU MUST APPLY IT EXACTLY AS REQUESTED. Do NOT evaluate its relevance to the job. If the user wants it, you MUST include it in the output.
2. EXTRACT EXISTING CONTEXT: After satisfying the user's explicit request, extract and formalize any existing certifications from the candidate's profile or existing sections.
3. ATS OPTIMIZATION: For the remaining content, ensure certifications are formatted professionally and highlight those relevant to the target job description.
4. DO NOT HALLUCINATE: Do not make up certifications that are not explicitly present in the provided context or requested by the user.
5. JSON SCHEMA: Output must exactly match the required JSON schema, containing the complete list of certifications.
"""),
    ("user", """
Candidate Information:
{candidate_info}

Target Job Information:
{job_info}

Existing Certifications (if any):
{existing_certifications}

User Request (What you need to do):
{user_request}
""")
])

from .utils import safe_state_node

@safe_state_node
def certification_generator_node(state: ResumeAgentState) -> ResumeAgentState:
    """Workflow node responsible for generating the Certifications section."""
    
    # Step 1 – Validate Invocation
    if not state.messages:
        return state
        
    latest_msg = state.messages[-1]
    if latest_msg.to_node != MessageSource.CERTIFICATION_GENERATOR or latest_msg.message_type != MessageType.WORKFLOW_REQUEST:
        return state

    # Step 2 – Gather Context
    try:
        candidate_data = json.loads(state.candidate_synthesis) if state.candidate_synthesis else {}
        onboarding_insights = candidate_data.get("onboarding_insights", {})
        onboarding_certs = onboarding_insights.get("certification_intelligence", [])
        candidate_info = json.dumps(onboarding_certs, indent=2)
    except Exception:
        candidate_info = state.candidate_synthesis
        onboarding_certs = []
        
    job_info = state.job_knowledge
    
    # Human-In-The-Loop check
    if not onboarding_certs and (not candidate_info or candidate_info.strip() in ["", "[]", "{}"]):
        # Check if the user already responded to our prompt
        user_response = None
        if len(state.messages) >= 2:
            prev_msg = state.messages[-2]
            if prev_msg.role == MessageRole.USER and prev_msg.message_type == MessageType.HUMAN_INPUT_RESPONSE:
                user_response = prev_msg.content

        # Check if the user requested to skip or remove this section in this turn
        user_msg = None
        for msg in reversed(state.messages):
            if msg.role == MessageRole.USER:
                user_msg = msg.content.lower()
                break

        if user_msg and (any(w in user_msg for w in ["remove all", "delete all", "clear all", "remove certification", "delete certification", "clear certification", "skip", "ignore", "don't have", "none"]) or user_msg in ["remove", "delete", "clear"]):
            logger.info("[Certification Workflow] User requested to remove/skip certifications section.")
            if not state.resume_content:
                state.resume_content = ResumeContent(sections=[])
            state.resume_content.sections = [s for s in state.resume_content.sections if s.section_type != ResumeSectionType.CERTIFICATIONS]
            
            completion_msg = ResumeMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
                role=MessageRole.ASSISTANT,
                message_type=MessageType.WORKFLOW_RESPONSE,
                from_node=MessageSource.CERTIFICATION_GENERATOR,
                to_node=MessageSource.INTENT_ROUTER,
                related_section=ResumeSectionType.CERTIFICATIONS,
                content="Removed the Certifications section as requested.",
                payload={"status": "COMPLETED"}
            )
            state.messages.append(completion_msg)
            return state
        elif user_response:
            candidate_info = f"User provided certifications details: {user_response}"
        else:
            logger.info("[Certification Workflow] Candidate info missing. Requesting human input.")
            new_msg = ResumeMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
                role=MessageRole.SYSTEM,
                message_type=MessageType.HUMAN_INPUT_REQUEST,
                from_node=MessageSource.CERTIFICATION_GENERATOR,
                to_node=MessageSource.USER,
                related_section=ResumeSectionType.CERTIFICATIONS,
                content="I don't have enough background information to write your certifications section. Could you please list your relevant certifications?",
                payload=None
            )
            state.messages.append(new_msg)
            return state

    existing_certifications = []
    if state.resume_content and state.resume_content.sections:
        for section in state.resume_content.sections:
            if section.section_type == ResumeSectionType.CERTIFICATIONS:
                existing_certifications = section.content
                break

    # Step 3 – Build Prompt & LLM Chain
    llm = get_structured_llm(CertificationsGenerationResponse)
    chain = CERTIFICATION_PROMPT | llm
    
    payload = {
        "candidate_info": candidate_info,
        "job_info": job_info or "General ATS optimized resume.",
        "existing_certifications": str(existing_certifications) if existing_certifications else "None.",
        "user_request": latest_msg.content
    }

    # Step 4 – Call the LLM
    try:
        output = chain.invoke(payload)
        
        # Step 5 – Validate Output
        if not isinstance(output, CertificationsGenerationResponse):
            raise ValueError("Output did not match CertificationsGenerationResponse schema.")
            
    except Exception as e:
        logger.error(f"[Certification Workflow] Generation failed: {e}")
        error_msg = ResumeMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            role=MessageRole.SYSTEM,
            message_type=MessageType.WORKFLOW_RESPONSE,
            from_node=MessageSource.CERTIFICATION_GENERATOR,
            to_node=MessageSource.INTENT_ROUTER,
            related_section=ResumeSectionType.CERTIFICATIONS,
            content=f"Certification generation failed: {e}",
            payload={"status": "FAILED"}
        )
        state.messages.append(error_msg)
        return state

    # Step 6 – Update Resume
    if not state.resume_content:
        state.resume_content = ResumeContent(sections=[])
        
    new_section = ResumeSection(
        section_type=ResumeSectionType.CERTIFICATIONS,
        display_name="Certifications",
        status=ResumeSectionState.COMPLETED,
        content=output.certifications
    )
    
    # Remove old certification section and append new
    state.resume_content.sections = [s for s in state.resume_content.sections if s.section_type != ResumeSectionType.CERTIFICATIONS]
    state.resume_content.sections.append(new_section)

    # Step 7 – Notify Completion
    completion_msg = ResumeMessage(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        role=MessageRole.ASSISTANT,
        message_type=MessageType.WORKFLOW_RESPONSE,
        from_node=MessageSource.CERTIFICATION_GENERATOR,
        to_node=MessageSource.INTENT_ROUTER,
        related_section=ResumeSectionType.CERTIFICATIONS,
        content=output.user_update_message,
        payload={"status": "COMPLETED"}
    )
    state.messages.append(completion_msg)

    # Step 8 – Return Updated State
    return state
