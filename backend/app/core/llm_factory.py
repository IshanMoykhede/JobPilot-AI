import os
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from pydantic import SecretStr

logger = logging.getLogger(__name__)

# Try to import settings, but fallback to os.getenv if circular
try:
    from app.core.config import settings
    gemini_key = settings.GEMINI_API_KEY
    groq_key = getattr(settings, "GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    llm_provider = getattr(settings, "LLM_PROVIDER", os.getenv("LLM_PROVIDER", "gemini"))
except ImportError:
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    llm_provider = os.getenv("LLM_PROVIDER", "gemini")

def get_llm(*args, **kwargs):
    """
    Initializes and returns an LLM instance. 
    Routes request based on LLM_PROVIDER or the explicit 'provider' override:
    - 'gemini': Returns the standard Gemini model (with Groq fallback if configured).
    - 'grok'/'groq': Returns a standalone ChatGroq model.
    """
    # Normalize model names
    model_name = kwargs.pop("model", None)
    fallback_model_name = kwargs.pop("fallback_model", "llama-3.1-8b-instant")
    explicit_provider = kwargs.pop("provider", None)
    
    # Remove key specific kwargs that might break other providers
    google_api_key = kwargs.pop("google_api_key", None)
    api_key = kwargs.pop("api_key", None)

    active_provider = explicit_provider or llm_provider

    # 1. Groq/Grok Provider Routing
    if active_provider in ("groq", "grok"):
        target_model = model_name or fallback_model_name
        current_groq_key = api_key or groq_key
        if not current_groq_key:
            raise ValueError("LLM provider is set to groq/grok but no GROQ_API_KEY is configured.")
        logger.info(f"[LLMFactory] Routing to Groq: model={target_model}")
        return ChatGroq(
            model=target_model,
            api_key=SecretStr(current_groq_key) if isinstance(current_groq_key, str) else current_groq_key,
            **kwargs
        )

    # 2. Default Gemini Provider with Groq Fallback
    target_gemini_model = model_name or "gemini-2.0-flash"
    
    if gemini_key and groq_key:
        try:
            gemini = ChatGoogleGenerativeAI(
                model=target_gemini_model,
                api_key=SecretStr(gemini_key),
                **kwargs
            )
            groq = ChatGroq(
                model=fallback_model_name,
                api_key=SecretStr(groq_key),
                **kwargs
            )
            logger.info(f"[LLMFactory] Routing to Gemini (with Groq fallback): model={target_gemini_model}")
            return gemini.with_fallbacks([groq])
        except Exception as e:
            logger.warning(f"Failed to initialize dual-LLM fallback: {e}")
            pass

    if gemini_key:
        try:
            logger.info(f"[LLMFactory] Routing to Gemini: model={target_gemini_model}")
            return ChatGoogleGenerativeAI(
                model=target_gemini_model,
                api_key=SecretStr(gemini_key),
                **kwargs
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini: {e}")
            pass

    if groq_key:
        logger.info(f"[LLMFactory] Routing to Groq standalone: model={fallback_model_name}")
        return ChatGroq(
            model=fallback_model_name,
            api_key=SecretStr(groq_key),
            **kwargs
        )
        
    raise ValueError("No valid LLM configuration found. Set GEMINI_API_KEY or GROQ_API_KEY.")

def get_structured_llm(schema, **kwargs):
    """
    Returns a Langchain Runnable that generates structured output matching the provided schema.
    It automatically routes to Gemini first, and if Gemini fails (e.g., rate limit, 429),
    it seamlessly falls back to Groq without crashing.
    """
    # Normalize model names
    model_name = kwargs.pop("model", "gemini-2.0-flash")
    fallback_model_name = kwargs.pop("fallback_model", "llama-3.1-8b-instant")
    explicit_provider = kwargs.pop("provider", None)
    
    active_provider = explicit_provider or llm_provider

    if active_provider in ("groq", "grok") or (not gemini_key and groq_key):
        if not groq_key:
            raise ValueError("No GROQ_API_KEY is configured.")
        logger.info(f"[LLMFactory] Creating structured LLM for Groq: model={fallback_model_name}")
        groq = ChatGroq(model=fallback_model_name, api_key=SecretStr(groq_key), **kwargs)
        return groq.with_structured_output(schema)

    if gemini_key and groq_key:
        try:
            logger.info(f"[LLMFactory] Creating structured LLM for Gemini (with Groq fallback): model={model_name}")
            gemini = ChatGoogleGenerativeAI(model=model_name, api_key=SecretStr(gemini_key), **kwargs)
            gemini_structured = gemini.with_structured_output(schema)
            
            groq = ChatGroq(model=fallback_model_name, api_key=SecretStr(groq_key), **kwargs)
            groq_structured = groq.with_structured_output(schema)
            
            return gemini_structured.with_fallbacks([groq_structured])
        except Exception as e:
            logger.warning(f"Failed to initialize dual-LLM structured fallback: {e}")
            pass

    if gemini_key:
        logger.info(f"[LLMFactory] Creating structured LLM for Gemini: model={model_name}")
        gemini = ChatGoogleGenerativeAI(model=model_name, api_key=SecretStr(gemini_key), **kwargs)
        return gemini.with_structured_output(schema)

    raise ValueError("No valid LLM configuration found for structured output.")


