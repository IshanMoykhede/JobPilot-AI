import logging
from typing import Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import get_structured_llm

from app.resume_tailoring_agent_v2.state import ResumeTailoringState

logger = logging.getLogger(__name__)

# 1. Output Schema
class RouterOutput(BaseModel):
    action: Literal["start_section", "revise_section", "approve_and_next", "finish"] = Field(
        description="The action to take next."
    )
    section: Optional[Literal[
        "basic_info", "summary", "experience", "education", 
        "skills", "projects", "certifications", "publications", 
        "awards", "volunteer"
    ]] = Field(default=None, description="The target section, if applicable.")


# 2. Router Prompt
ROUTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an Intent Router for a Resume Tailoring Agent. Determine the next action and target section based on the user's input.

Inputs provided to you:
- pending_sections: {pending_sections}
- current_section: {current_section}
- conversation_history (last 5 messages): {chat_history}

Action Rules:
- "start_section": User wants to begin a new section.
- "revise_section": User requests edits or gives feedback on the current draft.
- "approve_and_next": User approves the current draft and is ready to move on.
- "finish": User explicitly stops the process, or approves when pending_sections is empty."""),
    ("user", "{latest_message}")
])


def determine_intent(state: ResumeTailoringState) -> RouterOutput:
    """Invokes the LLM to route the user's intent."""
    if not state.messages:
        # Default start behavior if no messages exist
        first_section = state.pending_sections[0] if state.pending_sections else None
        return RouterOutput(action="start_section", section=first_section)
        
    # Extract latest message
    latest_message_dict = state.messages[-1]
    latest_message_content = latest_message_dict.get("content", "")
    
    # Format chat history (last 5 messages excluding the latest)
    recent_messages = state.messages[-6:-1]
    
    formatted_history = []
    for message in recent_messages:
        role = message.get("role", "unknown")
        content = message.get("content", "")
        formatted_history.append(f"{role.upper()}: {content}")
        
    formatted_chat_history = "\n".join(formatted_history) if formatted_history else "No prior context."
    
    try:
        llm = get_structured_llm(RouterOutput)
        chain = ROUTER_PROMPT | llm
        
        result = chain.invoke({
            "pending_sections": ", ".join(state.pending_sections) if state.pending_sections else "None",
            "current_section": state.current_section or "None",
            "chat_history": formatted_chat_history,
            "latest_message": latest_message_content
        })
        return result
        
    except Exception as e:
        logger.error(f"[V2 Router] Intent classification failed: {e}")
        # Failsafe fallback
        return RouterOutput(action="revise_section", section=state.current_section)

def intent_router_node(state: ResumeTailoringState) -> ResumeTailoringState:
    """LangGraph node that calls determine_intent and updates the state active_section."""
    logger.info("[V2] Executing intent_router_node")
    
    intent = determine_intent(state)
    
    # Handle state updates based on action
    if intent.action == "approve_and_next":
        # Remove the current section from pending list
        if state.current_section in state.pending_sections:
            state.pending_sections.remove(state.current_section)
            
        # Determine the next section automatically if the LLM didn't specify one
        # or if the specified one is already completed.
        if not intent.section or intent.section not in state.pending_sections:
            intent.section = state.pending_sections[0] if state.pending_sections else None
            
    # Simple routing logic for now: Just set active_section to whatever the user requested
    if intent.section:
        if intent.section not in ["summary", "projects", "skills", "experience", "education", "certifications", "general"]:
            # If it's something like "awards", map it to "custom:awards"
            state.active_section = f"custom:{intent.section}"
        else:
            state.active_section = intent.section
    else:
        state.active_section = "general"
        
    # Update current_section to track context
    state.current_section = intent.section
        
    return state
