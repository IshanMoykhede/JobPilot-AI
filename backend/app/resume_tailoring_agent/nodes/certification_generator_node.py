import uuid
import logging
import json
from typing import List
from datetime import datetime, timezone
from pydantic import BaseModel

from app.resume_tailoring_agent.state import ResumeAgentState
from app.resume_tailoring_agent.schemas.messaging import ResumeMessage, MessageRole, MessageType, MessageSource
from app.resume_tailoring_agent.schemas.common import ResumeSectionType, ResumeContent, ResumeSection, ResumeSectionState
from app.resume_tailoring_agent.schemas.certifications import CertificationEntry

from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import get_structured_llm

logger = logging.getLogger(__name__)

class CertificationSection(BaseModel):
    certifications: List[CertificationEntry]

CERTIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert ATS-optimized resume writer.
Your task is to generate or modify the Certifications section of the resume.

CRITICAL INSTRUCTIONS:
- Extract and formalize certifications from the candidate's background that are relevant to the target job.
- If the User Request asks to add, remove, modify, or replace a specific certification, strictly follow that request while keeping the rest of the existing certifications intact.
- Output must exactly match the required JSON schema, containing the complete list of certifications.
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
        candidate_info = json.dumps(candidate_data.get("certifications", candidate_data.get("Certification Intelligence", [])), indent=2)
    except Exception:
        candidate_info = state.candidate_synthesis
    job_info = state.job_knowledge
    
    # Human-In-The-Loop check
    if not candidate_info or candidate_info.strip() in ["", "[]", "{}"]:
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
    llm = get_structured_llm(CertificationSection)
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
        if not isinstance(output, CertificationSection):
            raise ValueError("Output did not match CertificationSection schema.")
            
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
        role=MessageRole.SYSTEM,
        message_type=MessageType.WORKFLOW_RESPONSE,
        from_node=MessageSource.CERTIFICATION_GENERATOR,
        to_node=MessageSource.INTENT_ROUTER,
        related_section=ResumeSectionType.CERTIFICATIONS,
        content="Successfully generated certifications section.",
        payload={"status": "COMPLETED"}
    )
    state.messages.append(completion_msg)

    # Step 8 – Return Updated State
    return state
