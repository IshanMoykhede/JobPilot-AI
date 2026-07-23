import uuid
import logging
from datetime import datetime, timezone

from app.resume_tailoring_agent.state import ResumeAgentState
from app.resume_tailoring_agent.schemas.messaging import ResumeMessage, MessageRole, MessageType, MessageSource
from app.resume_tailoring_agent.schemas.common import ResumeSectionType, ResumeContent, ResumeSection, ResumeSectionState
from app.resume_tailoring_agent.schemas.summary import ProfessionalSummary, SummaryGenerationResponse

from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import get_structured_llm


logger = logging.getLogger(__name__)

SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert ATS-optimized resume writer.
Your task is to generate a powerful, concise professional summary.

CRITICAL INSTRUCTIONS:
- Write a single paragraph (3-4 sentences max).
- Highlight key skills, years of experience, and a strong value proposition tailored to the target job.
- Do not use first-person pronouns (I, me, my).
- Output must exactly match the required JSON schema.
"""),
    ("user", """
Candidate Information:
{candidate_info}

Target Job Information:
{job_info}

Existing Summary (if any):
{existing_summary}
""")
])

def summary_generator_node(state: ResumeAgentState) -> ResumeAgentState:
    """Workflow node responsible for generating the Professional Summary."""
    
    # Step 1 – Validate Invocation
    if not state.messages:
        return state
        
    latest_msg = state.messages[-1]
    if latest_msg.to_node != MessageSource.SUMMARY_GENERATOR or latest_msg.message_type != MessageType.WORKFLOW_REQUEST:
        return state

    # Step 2 – Gather Context
    candidate_info = state.candidate_synthesis
    job_info = state.job_knowledge
    
    # Human-In-The-Loop check: Need at least some candidate info to generate a summary
    if not candidate_info or candidate_info.strip() == "" or candidate_info.strip() == "{}":
        logger.info("[Summary Workflow] Candidate info missing. Requesting human input.")
        new_msg = ResumeMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            role=MessageRole.SYSTEM,
            message_type=MessageType.HUMAN_INPUT_REQUEST,
            from_node=MessageSource.SUMMARY_GENERATOR,
            to_node=MessageSource.USER,
            related_section=ResumeSectionType.SUMMARY,
            content="I don't have enough background information to write a compelling summary. Could you please provide a brief overview of your career objective and experience?",
            payload=None
        )
        state.messages.append(new_msg)
        return state

    existing_summary = ""
    if state.resume_content and state.resume_content.sections:
        for section in state.resume_content.sections:
            if section.section_type == ResumeSectionType.SUMMARY:
                if isinstance(section.content, ProfessionalSummary):
                    existing_summary = section.content.content
                break

    # Step 3 – Build Prompt & LLM Chain
    llm = get_structured_llm(SummaryGenerationResponse)
    chain = SUMMARY_PROMPT | llm
    
    payload = {
        "candidate_info": candidate_info,
        "job_info": job_info or "General ATS optimized resume.",
        "existing_summary": existing_summary or "None."
    }

    # Step 4 – Call the LLM
    try:
        output = chain.invoke(payload)
        
        # Step 5 – Validate Output
        if not isinstance(output, SummaryGenerationResponse):
            raise ValueError("Output did not match SummaryGenerationResponse schema.")
            
    except Exception as e:
        logger.error(f"[Summary Workflow] Generation failed: {e}")
        error_msg = ResumeMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            role=MessageRole.SYSTEM,
            message_type=MessageType.WORKFLOW_RESPONSE,
            from_node=MessageSource.SUMMARY_GENERATOR,
            to_node=MessageSource.INTENT_ROUTER,
            related_section=ResumeSectionType.SUMMARY,
            content=f"Summary generation failed: {e}",
            payload={"status": "FAILED"}
        )
        state.messages.append(error_msg)
        return state

    # Step 6 – Update Resume
    if not state.resume_content:
        state.resume_content = ResumeContent(sections=[])
        
    new_section = ResumeSection(
        section_type=ResumeSectionType.SUMMARY,
        display_name="Professional Summary",
        status=ResumeSectionState.COMPLETED,
        content=output.summary
    )
    
    # Remove old summary and append new
    state.resume_content.sections = [s for s in state.resume_content.sections if s.section_type != ResumeSectionType.SUMMARY]
    state.resume_content.sections.append(new_section)

    # Step 7 – Notify Completion with AI Assistant Message
    completion_msg = ResumeMessage(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        role=MessageRole.ASSISTANT,
        message_type=MessageType.WORKFLOW_RESPONSE,
        from_node=MessageSource.SUMMARY_GENERATOR,
        to_node=MessageSource.INTENT_ROUTER,
        related_section=ResumeSectionType.SUMMARY,
        content=output.user_update_message,
        payload={"status": "COMPLETED"}
    )
    state.messages.append(completion_msg)

    # Step 8 – Return Updated State
    return state
