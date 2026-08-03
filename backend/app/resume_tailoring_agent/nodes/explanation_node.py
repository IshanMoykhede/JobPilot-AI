import logging
import uuid
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.llm_factory import get_llm
from app.resume_tailoring_agent.state import ResumeAgentState
from app.resume_tailoring_agent.schemas.messaging import ResumeMessage, MessageRole, MessageType, MessageSource

logger = logging.getLogger(__name__)

EXPLANATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a polite, helpful, and conversational AI assistant helping a user build their resume.
You are given structured generator metadata.

Never infer anything outside this metadata. Explain the situation ONLY using the metadata provided. Do not invent reasons.

RULES FOR 'WAITING_FOR_USER' STATUS:
- The generator was unable to proceed because it needs more information.
- Ask the `user_question` naturally and politely.
- Do NOT talk about changes, because no changes were made.

RULES FOR 'COMPLETED' STATUS:
- The generator successfully updated the resume section!
- Explain exactly what improvements were made using the `summary` and `changes`.
- Mention the `next_section` to the user and ask if they would like to continue to it.

You must output ONLY the conversational text you want to send to the user. Do not output JSON. Do not include internal thoughts.
"""),
    ("user", """
Generator Metadata:
{metadata_json}

Next Section To Work On:
{next_section}

Write the conversational response now:
""")
])

def explanation_node(state: ResumeAgentState) -> ResumeAgentState:
    logger.info("[Explanation Node] Generating explanation from metadata...")
    
    if not state.latest_generation or not state.latest_generation.metadata:
        logger.warning("[Explanation Node] No latest_generation metadata found. Skipping explanation.")
        state.next_node = "response_node"
        return state
        
    metadata = state.latest_generation.metadata
    
    # Calculate next_section in Python, keep the LLM dumb
    next_section = None
    if state.pending_sections:
        pending_without_summary = [s for s in state.pending_sections if s != "SUMMARY"]
        if pending_without_summary:
            next_section = pending_without_summary[0]
        elif "SUMMARY" in state.pending_sections:
            next_section = "SUMMARY"
            
    payload = {
        "metadata_json": metadata.model_dump_json(indent=2),
        "next_section": next_section or "None (All done!)"
    }
    
    try:
        # Generate conversational text
        llm = get_llm()
        chain = EXPLANATION_PROMPT | llm | StrOutputParser()
        conversational_text = chain.invoke(payload)
        
        # Create ResumeMessage to append to state
        new_msg = ResumeMessage(
            id=uuid.uuid4().hex,
            timestamp=datetime.utcnow().isoformat() + "Z",
            role=MessageRole.ASSISTANT,
            message_type=MessageType.HUMAN_INPUT_REQUEST if metadata.status == "WAITING_FOR_USER" else MessageType.WORKFLOW_RESPONSE,
            from_node=MessageSource.SYSTEM,
            to_node=MessageSource.USER,
            content=conversational_text
        )
        
        if not state.messages:
            state.messages = []
            
        # Pydantic states in LangGraph usually require dumping or storing as objects. 
        # state.messages is list[dict] or list[ResumeMessage]. Assuming list[ResumeMessage] or list[dict].
        # Let's dump it to dict to be safe if LangGraph is expecting JSONable dicts, 
        # or just append the model. We'll append the dict.
        state.messages.append(new_msg.model_dump())
        
        logger.info("[Explanation Node] Successfully generated explanation and appended to messages.")
        
    except Exception as e:
        logger.error(f"[Explanation Node] Failed to generate explanation: {e}")
        
    # We DO NOT clear state.latest_generation here so it isn't lost on crash.
    # The next generator will safely overwrite it.
    
    return state
