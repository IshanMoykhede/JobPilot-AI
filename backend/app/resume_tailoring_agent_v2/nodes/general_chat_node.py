import logging
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import get_llm
from app.resume_tailoring_agent_v2.state import ResumeTailoringState

logger = logging.getLogger(__name__)

# General Chat Prompt
GENERAL_CHAT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are the friendly AI Resume Tailoring Assistant. The user is asking a general question, checking progress, or making casual conversation rather than focusing on a specific resume section.

Current Progress:
- Completed Sections (Drafts saved): {completed_sections}
- Sections Remaining (Pending): {pending_sections}

Guidelines:
- Answer the user's question politely and concisely.
- Keep them updated on what has been done and what is left.
- If they are completely finished (0 pending sections), congratulate them on finishing their resume!
- DO NOT generate a resume section draft here. Just reply directly in a conversational tone."""),
    ("user", "{latest_message}")
])

def general_chat_node(state: ResumeTailoringState) -> ResumeTailoringState:
    """Handles general conversational intent when no specific section is active."""
    logger.info("[V2] Executing general_chat_node")
    
    # Get latest message
    latest_message_content = ""
    if state.messages:
        latest_message_content = state.messages[-1].get("content", "")
        
    completed_sections = list(state.drafts.keys()) if state.drafts else ["None"]
    pending_sections = state.pending_sections if state.pending_sections else ["None - You are completely finished!"]
    
    try:
        # Standard unstructured LLM invocation
        llm = get_llm()
        chain = GENERAL_CHAT_PROMPT | llm
        
        result = chain.invoke({
            "completed_sections": ", ".join(completed_sections),
            "pending_sections": ", ".join(pending_sections),
            "latest_message": latest_message_content
        })
        
        # result is an AIMessage, get the string content
        assistant_reply = result.content
        
        state.messages.append({
            "role": "assistant",
            "content": assistant_reply
        })
        
        return state
        
    except Exception as e:
        logger.error(f"[V2 General Chat Node] Failed to generate chat response: {e}")
        state.messages.append({
            "role": "assistant",
            "content": "I'm here to help! We've made great progress. What would you like to do next?"
        })
        return state
