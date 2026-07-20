import os
import logging
from langchain_groq import ChatGroq
from pydantic import SecretStr

logger = logging.getLogger(__name__)

# Try to import settings, but fallback to os.getenv if circular
try:
    from app.core.config import settings
    groq_key = getattr(settings, "GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
except ImportError:
    groq_key = os.getenv("GROQ_API_KEY")

def get_llm(*args, **kwargs):
    """
    Initializes and returns a Groq LLM instance.
    """
    # Normalize model names
    model_name = kwargs.pop("model", None)
    fallback_model_name = kwargs.pop("fallback_model", "llama-3.3-70b-versatile")
    
    # Remove key specific kwargs that might break providers
    kwargs.pop("provider", None)
    kwargs.pop("google_api_key", None)
    api_key = kwargs.pop("api_key", None)

    target_model = model_name or fallback_model_name
    current_groq_key = api_key or groq_key
    
    if not current_groq_key:
        raise ValueError("No GROQ_API_KEY is configured.")
        
    logger.info(f"[LLMFactory] Routing to Groq: model={target_model}")
    return ChatGroq(
        model=target_model,
        api_key=SecretStr(current_groq_key) if isinstance(current_groq_key, str) else current_groq_key,
        **kwargs
    )

def get_structured_llm(schema, **kwargs):
    """
    Returns a Langchain Runnable that generates structured output matching the provided schema using Groq.
    """
    # Normalize model names
    model_name = kwargs.pop("model", "llama-3.3-70b-versatile")
    fallback_model_name = kwargs.pop("fallback_model", "llama-3.1-8b-instant")
    kwargs.pop("provider", None)
    kwargs.pop("google_api_key", None)
    
    if not groq_key:
        raise ValueError("No GROQ_API_KEY is configured.")
        
    logger.info(f"[LLMFactory] Creating structured LLM for Groq: model={model_name}")
    groq = ChatGroq(model=model_name, api_key=SecretStr(groq_key), **kwargs)
    return groq.with_structured_output(schema)
