import uuid
from datetime import datetime, timezone
from typing import Optional
from app.resume_tailoring_agent.state import ResumeAgentState
from app.resume_tailoring_agent.schemas.messaging import ResumeMessage, MessageRole, MessageType, MessageSource
from app.resume_tailoring_agent.schemas.common import ResumeSectionType

def detect_intent(text: str) -> str:
    """Extremely simple deterministic intent detection for MVP."""
    text = text.lower()
    
    if "download" in text or "pdf" in text:
        return "DOWNLOAD_RESUME"
    if "summary" in text:
        return "MODIFY_SUMMARY"
    if "project" in text:
        return "MODIFY_PROJECT"
    if "experience" in text or "job" in text:
        return "MODIFY_EXPERIENCE"
    if "skill" in text:
        return "MODIFY_SKILLS"
    if "education" in text or "degree" in text or "university" in text:
        return "MODIFY_EDUCATION"
    if "continue" in text:
        return "CONTINUE_WORKFLOW"
        
    return "GENERATE_RESUME"

def _get_node_for_section(section: ResumeSectionType) -> MessageSource:
    mapping = {
        ResumeSectionType.SUMMARY: MessageSource.SUMMARY_GENERATOR,
        ResumeSectionType.PROJECTS: MessageSource.PROJECT_GENERATOR,
        ResumeSectionType.EXPERIENCE: MessageSource.EXPERIENCE_GENERATOR,
        ResumeSectionType.SKILLS: MessageSource.SKILLS_GENERATOR,
        ResumeSectionType.EDUCATION: MessageSource.EDUCATION_GENERATOR,
        ResumeSectionType.CERTIFICATIONS: MessageSource.CERTIFICATION_GENERATOR
    }
    return mapping.get(section, MessageSource.SYSTEM)

def _create_routing_message(to_node: MessageSource, content: str, related_section: Optional[ResumeSectionType]) -> ResumeMessage:
    return ResumeMessage(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        role=MessageRole.SYSTEM,
        message_type=MessageType.WORKFLOW_REQUEST,
        from_node=MessageSource.INTENT_ROUTER,
        to_node=to_node,
        related_section=related_section,
        content=content,
        payload=None
    )

def intent_router_node(state: ResumeAgentState) -> ResumeAgentState:
    """Central orchestrator for the Resume Tailoring Agent."""
    if not state.messages:
        return state
        
    latest_msg = state.messages[-1]
    
    # 1. Handle User Query
    if latest_msg.role == MessageRole.USER:
        # Check if we were waiting for user input
        if state.current_section and any(m.message_type == MessageType.HUMAN_INPUT_REQUEST for m in state.messages[-3:]):
            next_node = _get_node_for_section(state.current_section)
            new_msg = _create_routing_message(next_node, "User provided requested information.", state.current_section)
            state.messages.append(new_msg)
            return state

        intent = detect_intent(latest_msg.content)
        
        if intent == "DOWNLOAD_RESUME":
            new_msg = _create_routing_message(MessageSource.PDF_GENERATOR, "Generate PDF.", None)
            state.messages.append(new_msg)
            return state
            
        if intent == "MODIFY_SUMMARY":
            new_msg = _create_routing_message(MessageSource.SUMMARY_GENERATOR, "Modify the summary section.", ResumeSectionType.SUMMARY)
            state.current_section = ResumeSectionType.SUMMARY
            state.messages.append(new_msg)
            return state
            
        if intent == "MODIFY_PROJECT":
            new_msg = _create_routing_message(MessageSource.PROJECT_GENERATOR, "Modify the project section.", ResumeSectionType.PROJECTS)
            state.current_section = ResumeSectionType.PROJECTS
            state.messages.append(new_msg)
            return state
            
        if intent == "MODIFY_EXPERIENCE":
            new_msg = _create_routing_message(MessageSource.EXPERIENCE_GENERATOR, "Modify the experience section.", ResumeSectionType.EXPERIENCE)
            state.current_section = ResumeSectionType.EXPERIENCE
            state.messages.append(new_msg)
            return state
            
        if intent == "MODIFY_SKILLS":
            new_msg = _create_routing_message(MessageSource.SKILLS_GENERATOR, "Modify the skills section.", ResumeSectionType.SKILLS)
            state.current_section = ResumeSectionType.SKILLS
            state.messages.append(new_msg)
            return state
            
        if intent == "MODIFY_EDUCATION":
            new_msg = _create_routing_message(MessageSource.EDUCATION_GENERATOR, "Modify the education section.", ResumeSectionType.EDUCATION)
            state.current_section = ResumeSectionType.EDUCATION
            state.messages.append(new_msg)
            return state
            
        if intent == "GENERATE_RESUME" or intent == "CONTINUE_WORKFLOW":
            if state.pending_sections:
                next_section = state.pending_sections[0]
                next_node = _get_node_for_section(next_section)
                new_msg = _create_routing_message(next_node, f"Generate the {next_section.value} section.", next_section)
                state.current_section = next_section
                state.messages.append(new_msg)
                return state
            else:
                new_msg = _create_routing_message(MessageSource.SYSTEM, "Resume generation complete.", None)
                state.response_message = "Your resume has been completely generated."
                state.messages.append(new_msg)
                return state

    # 2. Handle Workflow Responses
    if latest_msg.message_type == MessageType.WORKFLOW_RESPONSE:
        payload = latest_msg.payload or {}
        status = payload.get("status")
        
        if status == "WAITING_FOR_USER":
            new_msg = _create_routing_message(MessageSource.SYSTEM, "Waiting for user input.", latest_msg.related_section)
            state.response_message = latest_msg.content
            state.messages.append(new_msg)
            return state
            
        if status == "COMPLETED":
            if latest_msg.related_section in state.pending_sections:
                state.pending_sections.remove(latest_msg.related_section)
                
            if state.pending_sections:
                next_section = state.pending_sections[0]
                next_node = _get_node_for_section(next_section)
                new_msg = _create_routing_message(next_node, f"Generate the {next_section.value} section.", next_section)
                state.current_section = next_section
                state.messages.append(new_msg)
                return state
            else:
                new_msg = _create_routing_message(MessageSource.SYSTEM, "All sections completed.", None)
                state.response_message = "All sections have been completed successfully."
                state.current_section = None
                state.messages.append(new_msg)
                return state
                
    return state
