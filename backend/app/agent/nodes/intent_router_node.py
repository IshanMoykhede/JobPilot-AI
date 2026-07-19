import logging
from pydantic import BaseModel, Field
from app.core.llm_factory import get_llm
from pydantic import SecretStr


from app.core.config import settings
from app.agent.schemas.agent_state import AgentState
from app.agent.core.agent_enums import Intent
from app.agent.core import agent_config, agent_constants

logger = logging.getLogger(__name__)

class IntentClassification(BaseModel):
    intent: Intent = Field(..., description="The classified intent of the user query.")

async def intent_router_node(state: AgentState) -> dict:
    """
    Determines the intent of the user query using Gemini and writes it to the graph state.
    Falls back to Groq if Gemini hits rate limits (RESOURCE_EXHAUSTED).
    Contains no business logic.
    """
    user_query = state.get("user_query", "")
    print(f"\n[{'='*50}]")
    print(f"--> ENTERING INTENT ROUTER")
    print(f"--> User Query: '{user_query}'")
    logger.info(f"[IntentRouterNode] Classifying query: '{user_query[:50]}...'")

    if not user_query.strip():
        logger.warning("[IntentRouterNode] Empty query received, defaulting to UNKNOWN.")
        return {"intent": Intent.UNKNOWN.value}

    if not settings.GEMINI_API_KEY:
        logger.warning("[IntentRouterNode] No Gemini API key found, defaulting to JOB_SEARCH.")
        return {"intent": Intent.JOB_SEARCH.value}

    try:
        provider = getattr(settings, "LLM_PROVIDER", "gemini")
        if provider in ("groq", "grok"):
            llm = get_llm(
                provider="groq",
                model="llama-3.1-8b-instant",
                temperature=agent_config.AGENT_TEMPERATURE
            )
        else:
            # Primary LLM: Gemini
            llm = get_llm(
                provider="gemini",
                model=agent_config.AGENT_MODEL,
                temperature=agent_config.AGENT_TEMPERATURE,
                max_retries=1 # Fail fast on rate limits to trigger fallback
            )
            
            # Fallback LLM: Groq (Llama-3-8B is lightning fast for routing)
            if settings.GROQ_API_KEY:
                groq_llm = get_llm(
                    provider="groq",
                    model="llama-3.1-8b-instant",
                    temperature=agent_config.AGENT_TEMPERATURE,
                    max_retries=1 # Prevent burning through strict capacity limits
                )
                # Apply fallback routing
                llm = llm.with_fallbacks([groq_llm])
        
        structured_llm = llm.with_structured_output(IntentClassification)
        prompt = agent_constants.INTENT_ROUTER_PROMPT.format(user_query=user_query)
        
        response = await structured_llm.ainvoke(prompt)
        intent = response.intent.value
        
        print(f"--> Output Intent: {intent}")
        print(f"[{'='*50}]\n")
        logger.info(f"[IntentRouterNode] Classified intent: {intent}")
        return {"intent": intent}
        
    except Exception as e:
        logger.error(f"[IntentRouterNode] Failed to classify intent: {e}")
        # Route to fallback in case of errors
        return {"intent": Intent.UNKNOWN.value}
