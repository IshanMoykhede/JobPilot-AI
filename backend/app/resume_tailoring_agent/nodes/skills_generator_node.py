import uuid
import logging
import json
from typing import List
from datetime import datetime, timezone
from pydantic import BaseModel

from app.resume_tailoring_agent.state import ResumeAgentState
from app.resume_tailoring_agent.schemas.messaging import ResumeMessage, MessageRole, MessageType, MessageSource
from app.resume_tailoring_agent.schemas.common import ResumeSectionType, ResumeContent, ResumeSection, ResumeSectionState
from app.resume_tailoring_agent.schemas.skills import SkillCategory, SkillsGenerationResponse

from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import get_structured_llm

logger = logging.getLogger(__name__)

SKILLS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert ATS-optimized resume writer.
Your task is to generate or modify the Skills section of the resume.

CRITICAL INSTRUCTIONS:
- Categorize skills logically (e.g., Languages, Frameworks, Tools, etc.)
- Ensure the skills align closely with the target job requirements.
- If the User Request asks to add, remove, modify, or replace a specific skill, strictly follow that request while keeping the rest of the existing skills intact.
- Output must exactly match the required JSON schema, containing the complete list of skill categories.
"""),
    ("user", """
Candidate Information:
{candidate_info}

Target Job Information:
{job_info}

Existing Skills (if any):
{existing_skills}

User Request (What you need to do):
{user_request}
""")
])

def skills_generator_node(state: ResumeAgentState) -> ResumeAgentState:
    """Workflow node responsible for generating the Skills section."""
    
    # Step 1 – Validate Invocation
    if not state.messages:
        return state
        
    latest_msg = state.messages[-1]
    if latest_msg.to_node != MessageSource.SKILLS_GENERATOR or latest_msg.message_type != MessageType.WORKFLOW_REQUEST:
        return state

    # Step 2 – Gather Context
    try:
        candidate_data = json.loads(state.candidate_synthesis) if state.candidate_synthesis else {}
        candidate_info = json.dumps(candidate_data.get("skills", candidate_data.get("Skill Intelligence", [])), indent=2)
    except Exception:
        candidate_info = state.candidate_synthesis
    job_info = state.job_knowledge
    
    # Human-In-The-Loop check
    if not candidate_info or candidate_info.strip() in ["", "[]", "{}"]:
        logger.info("[Skills Workflow] Candidate info missing. Requesting human input.")
        new_msg = ResumeMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            role=MessageRole.SYSTEM,
            message_type=MessageType.HUMAN_INPUT_REQUEST,
            from_node=MessageSource.SKILLS_GENERATOR,
            to_node=MessageSource.USER,
            related_section=ResumeSectionType.SKILLS,
            content="I don't have enough background information to write your skills section. Could you please list your technical and professional skills?",
            payload=None
        )
        state.messages.append(new_msg)
        return state

    existing_skills = []
    if state.resume_content and state.resume_content.sections:
        for section in state.resume_content.sections:
            if section.section_type == ResumeSectionType.SKILLS:
                existing_skills = section.content
                break

    # Step 3 – Build Prompt & LLM Chain
    llm = get_structured_llm(SkillsGenerationResponse)
    chain = SKILLS_PROMPT | llm
    
    payload = {
        "candidate_info": candidate_info,
        "job_info": job_info or "General ATS optimized resume.",
        "existing_skills": str(existing_skills) if existing_skills else "None.",
        "user_request": latest_msg.content
    }

    # Step 4 – Call the LLM
    try:
        output = chain.invoke(payload)
        
        # Step 5 – Validate Output
        if not isinstance(output, SkillsGenerationResponse):
            raise ValueError("Output did not match SkillsGenerationResponse schema.")
            
    except Exception as e:
        logger.error(f"[Skills Workflow] Generation failed: {e}")
        error_msg = ResumeMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            role=MessageRole.SYSTEM,
            message_type=MessageType.WORKFLOW_RESPONSE,
            from_node=MessageSource.SKILLS_GENERATOR,
            to_node=MessageSource.INTENT_ROUTER,
            related_section=ResumeSectionType.SKILLS,
            content=f"Skills generation failed: {e}",
            payload={"status": "FAILED"}
        )
        state.messages.append(error_msg)
        return state

    # Step 6 – Update Resume
    if not state.resume_content:
        state.resume_content = ResumeContent(sections=[])
        
    new_section = ResumeSection(
        section_type=ResumeSectionType.SKILLS,
        display_name="Skills",
        status=ResumeSectionState.COMPLETED,
        content=output.skills
    )
    
    # Remove old skills section and append new
    state.resume_content.sections = [s for s in state.resume_content.sections if s.section_type != ResumeSectionType.SKILLS]
    state.resume_content.sections.append(new_section)

    # Step 7 – Notify Completion
    completion_msg = ResumeMessage(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        role=MessageRole.ASSISTANT,
        message_type=MessageType.WORKFLOW_RESPONSE,
        from_node=MessageSource.SKILLS_GENERATOR,
        to_node=MessageSource.INTENT_ROUTER,
        related_section=ResumeSectionType.SKILLS,
        content=output.user_update_message,
        payload={"status": "COMPLETED"}
    )
    state.messages.append(completion_msg)

    # Step 8 – Return Updated State
    return state
