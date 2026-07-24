import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import get_structured_llm

from app.resume_tailoring_agent.state import ResumeAgentState
from app.resume_tailoring_agent.schemas.messaging import ResumeMessage, MessageRole, MessageType, MessageSource
from app.resume_tailoring_agent.schemas.common import ResumeSectionType, ResumeContent

logger = logging.getLogger(__name__)

# 1. Classification Schema for Intent Routing
class RouterClassification(BaseModel):
    action_type: str = Field(
        description="One of: GENERATE_ALL, REGENERATE_ALL, MODIFY_SECTION, DELETE_SECTION, DOWNLOAD_RESUME, CONVERSATIONAL"
    )
    target_sections: List[str] = Field(
        description="Affected sections, e.g. ['PROJECTS', 'EXPERIENCE']. Must be subset of: SUMMARY, PROJECTS, EXPERIENCE, SKILLS, EDUCATION, CERTIFICATIONS, CO_CURRICULAR. Empty for GENERATE_ALL, REGENERATE_ALL, DOWNLOAD_RESUME, or CONVERSATIONAL."
    )
    conversational_reply: Optional[str] = Field(
        description="A friendly, helpful response answering the user directly. ONLY populate this field if action_type is 'CONVERSATIONAL'."
    )

# 2. Orchestration Prompt
ROUTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the orchestration router for an AI Resume Tailoring Assistant.
Your task is to classify the user's query and output a structured routing plan.

Action Types:
1. 'GENERATE_ALL': The user wants to start tailoring, generate the entire resume from scratch, or begin a fresh optimization run (e.g. "generate resume", "tailor my resume", "optimize for this job").
2. 'REGENERATE_ALL': The user wants to regenerate all sections of the resume again (e.g. "regenerate all", "redo the whole resume", "start over").
3. 'MODIFY_SECTION': The user wants to add, edit, change, replace, or update one or more specific sections (e.g. "modify only my projects", "add a project", "replace my education", "update experience").
4. 'DELETE_SECTION': The user wants to remove, delete, exclude, or hide a specific section (e.g. "remove my projects section", "clear education", "delete certifications").
5. 'DOWNLOAD_RESUME': The user wants to download, export, print, or get the PDF version of their resume.
6. 'CONVERSATIONAL': The user is greeting you ("hi", "hello"), asking a general question ("how does this work?", "what models do you use?"), making a general comment, or checking status. You must reply in 'conversational_reply'.

Allowed Target Sections:
- 'SUMMARY'
- 'PROJECTS'
- 'EXPERIENCE'
- 'SKILLS'
- 'EDUCATION'
- 'CERTIFICATIONS'
- 'CO_CURRICULAR'

Recent Chat Context:
{chat_history}
"""),
    ("user", "User Query: {query}")
])

def detect_intent_llm(text: str, chat_history: str = "") -> RouterClassification:
    """Invokes LLM for structured intent routing with a robust local fallback."""
    try:
        llm = get_structured_llm(RouterClassification)
        chain = ROUTER_PROMPT | llm
        return chain.invoke({"query": text, "chat_history": chat_history})
    except Exception as e:
        logger.error(f"[Router LLM] Structured classification failed: {e}")
        text_lower = text.lower()
        if "download" in text_lower or "pdf" in text_lower:
            return RouterClassification(action_type="DOWNLOAD_RESUME", target_sections=[])
        if any(w in text_lower for w in ["remove", "delete", "clear", "exclude"]):
            for sec in ["PROJECTS", "EXPERIENCE", "SKILLS", "EDUCATION", "CERTIFICATIONS"]:
                if sec.lower() in text_lower:
                    return RouterClassification(action_type="DELETE_SECTION", target_sections=[sec])
            # If no specific section found but they want to delete/clear
            return RouterClassification(action_type="CONVERSATIONAL", target_sections=[], conversational_reply="Which section would you like me to remove?")
        if "regenerate" in text_lower or "start over" in text_lower or "redo" in text_lower:
            return RouterClassification(action_type="REGENERATE_ALL", target_sections=[])
        for sec in ["PROJECTS", "EXPERIENCE", "SKILLS", "EDUCATION", "CERTIFICATIONS"]:
            if sec.lower() in text_lower:
                return RouterClassification(action_type="MODIFY_SECTION", target_sections=[sec])
        return RouterClassification(action_type="GENERATE_ALL", target_sections=[])

def _get_node_for_section(section_str: str) -> MessageSource:
    mapping = {
        "PROJECTS": MessageSource.PROJECT_GENERATOR,
        "EXPERIENCE": MessageSource.EXPERIENCE_GENERATOR,
        "SKILLS": MessageSource.SKILLS_GENERATOR,
        "EDUCATION": MessageSource.EDUCATION_GENERATOR,
        "CERTIFICATIONS": MessageSource.CERTIFICATION_GENERATOR,
        "CO_CURRICULAR": MessageSource.CO_CURRICULAR_GENERATOR,
    }
    return mapping.get(section_str.upper(), MessageSource.SYSTEM)

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

from .utils import safe_state_node

@safe_state_node
def intent_router_node(state: ResumeAgentState) -> ResumeAgentState:
    """Central orchestrator for the Resume Tailoring Agent."""
    # Failsafe: Remove SUMMARY from legacy states to prevent routing loops
    if "SUMMARY" in state.pending_sections:
        state.pending_sections.remove("SUMMARY")
    if "summary" in state.pending_sections:
        state.pending_sections.remove("summary")
        
    if not state.messages:
        return state
        
    latest_msg = state.messages[-1]
    
    # 1. Handle User Query
    if latest_msg.role == MessageRole.USER:
        # Check if we were waiting for user input
        if state.current_section and any(m.message_type == MessageType.HUMAN_INPUT_REQUEST for m in state.messages[-3:]):
            next_node = _get_node_for_section(state.current_section)
            new_msg = _create_routing_message(next_node, "User provided requested information.", ResumeSectionType(state.current_section))
            state.messages.append(new_msg)
            return state

        # Call structured classification
        recent_msgs = []
        for m in reversed(state.messages[:-1]):
            if len(recent_msgs) >= 3:
                break
            if m.role in [MessageRole.USER, MessageRole.ASSISTANT]:
                recent_msgs.insert(0, f"{m.role.value.upper()}: {m.content}")
        chat_history = "\n".join(recent_msgs) if recent_msgs else "No prior context."
        
        classification = detect_intent_llm(latest_msg.content, chat_history=chat_history)
        logger.info(f"[Router LLM] Classified intent: {classification.action_type} - Targets: {classification.target_sections}")

        if classification.action_type == "MODIFY_SECTION" and not classification.target_sections:
            logger.warning("[Router] MODIFY_SECTION but no target_sections! Falling back to asking user.")
            new_msg = ResumeMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
                role=MessageRole.ASSISTANT,
                message_type=MessageType.SYSTEM_NOTIFICATION,
                from_node=MessageSource.INTENT_ROUTER,
                to_node=MessageSource.USER,
                content="Which section would you like to modify?",
                payload=None
            )
            state.messages.append(new_msg)
            return state

        if classification.action_type == "DOWNLOAD_RESUME":
            new_msg = _create_routing_message(MessageSource.PDF_GENERATOR, "Generate PDF.", None)
            state.messages.append(new_msg)
            return state

        if classification.action_type == "CONVERSATIONAL":
            new_msg = ResumeMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
                role=MessageRole.ASSISTANT,
                message_type=MessageType.SYSTEM_NOTIFICATION,
                from_node=MessageSource.INTENT_ROUTER,
                to_node=MessageSource.USER,
                content=classification.conversational_reply or "Sure, how can I help you tailoring your resume today?",
                payload=None
            )
            state.messages.append(new_msg)
            return state

        if classification.action_type == "DELETE_SECTION":
            for sec_name in classification.target_sections:
                sec_type_val = ResumeSectionType(sec_name.upper())
                if state.resume_content and "sections" in state.resume_content:
                    state.resume_content["sections"] = [s for s in state.resume_content["sections"] if s.get("section_type") != sec_type_val.value]
                if sec_type_val.value in state.pending_sections:
                    state.pending_sections.remove(sec_type_val.value)
            
            removal_desc = ", ".join(classification.target_sections)
            new_msg = ResumeMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
                role=MessageRole.ASSISTANT,
                message_type=MessageType.SYSTEM_NOTIFICATION,
                from_node=MessageSource.INTENT_ROUTER,
                to_node=MessageSource.USER,
                content=f"Removed the {removal_desc} section(s) as requested.",
                payload=None
            )
            state.messages.append(new_msg)
            state.response_message = f"Removed the {removal_desc} section(s)."
            state.current_section = None
            return state

        if classification.action_type == "REGENERATE_ALL":
            state.pending_sections = [
                ResumeSectionType.PROJECTS.value,
                ResumeSectionType.EXPERIENCE.value,
                ResumeSectionType.SKILLS.value,
                ResumeSectionType.EDUCATION.value,
                ResumeSectionType.CERTIFICATIONS.value,
                ResumeSectionType.CO_CURRICULAR.value,
                ResumeSectionType.SUMMARY.value
            ]
            # Retain only Personal Information
            if state.resume_content and "sections" in state.resume_content:
                state.resume_content["sections"] = [s for s in state.resume_content["sections"] if s.get("section_type") == ResumeSectionType.PERSONAL_INFORMATION.value]
            
            startup_msg = ResumeMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
                role=MessageRole.ASSISTANT,
                message_type=MessageType.SYSTEM_NOTIFICATION,
                from_node=MessageSource.INTENT_ROUTER,
                to_node=MessageSource.USER,
                content="Starting complete regeneration of all sections of your resume...",
                payload=None
            )
            state.messages.append(startup_msg)
            
            next_section = state.pending_sections[0]
            next_node = _get_node_for_section(next_section.upper())
            new_msg = _create_routing_message(next_node, f"Generate the {next_section} section.", ResumeSectionType(next_section))
            state.current_section = next_section
            state.messages.append(new_msg)
            return state

        if classification.action_type == "MODIFY_SECTION" and classification.target_sections:
            target_str_list = [sec.upper() for sec in classification.target_sections]
            state.pending_sections = target_str_list
            
            next_section = state.pending_sections[0]
            next_node = _get_node_for_section(next_section.upper())
            new_msg = _create_routing_message(next_node, f"Modify the {next_section} section.", ResumeSectionType(next_section.upper()))
            state.current_section = next_section
            state.messages.append(new_msg)
            return state

        # Default action: GENERATE_ALL
        if state.pending_sections:
            sections_list = ", ".join(state.pending_sections)
            startup_msg = ResumeMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
                role=MessageRole.ASSISTANT,
                message_type=MessageType.SYSTEM_NOTIFICATION,
                from_node=MessageSource.INTENT_ROUTER,
                to_node=MessageSource.USER,
                content=f"I'm optimizing these sections for you: {sections_list}.",
                payload=None
            )
            state.messages.append(startup_msg)

            next_section = state.pending_sections[0]
            next_node = _get_node_for_section(next_section.upper())
            new_msg = _create_routing_message(next_node, f"Generate the {next_section} section.", ResumeSectionType(next_section.upper()))
            state.current_section = next_section
            state.messages.append(new_msg)
            return state
        else:
            new_msg = _create_routing_message(MessageSource.SYSTEM, "Resume generation complete.", None)
            state.response_message = "Your resume has been completely generated."
            state.messages.append(new_msg)
            return state

    # 2. Handle Workflow Responses from generator nodes
    if latest_msg.message_type == MessageType.WORKFLOW_RESPONSE:
        payload = latest_msg.payload or {}
        status = payload.get("status")
        
        if status == "WAITING_FOR_USER":
            new_msg = _create_routing_message(MessageSource.SYSTEM, "Waiting for user input.", ResumeSectionType(latest_msg.related_section))
            state.response_message = latest_msg.content
            state.messages.append(new_msg)
            return state
            
        if status == "COMPLETED":
            rel_sec_val = latest_msg.related_section.value if latest_msg.related_section else ""
            if rel_sec_val in state.pending_sections:
                state.pending_sections.remove(rel_sec_val)
                
            if state.pending_sections:
                next_section = state.pending_sections[0]
                next_node = _get_node_for_section(next_section.upper())
                new_msg = _create_routing_message(next_node, f"Generate the {next_section} section.", ResumeSectionType(next_section))
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
