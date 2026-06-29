import logging
from pydantic import ValidationError

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.exceptions import OutputParserException

from app.core.config import settings
from app.schemas.candidate_profile import ResumeDataSchema
from pydantic import SecretStr
from typing import cast

logger = logging.getLogger(__name__)

class ResumeParserService:
    _groq_chain = None
    _gemini_chain = None

    @classmethod
    def _get_chains(cls):
        """Initializes and caches LLM chains globally."""
        if cls._groq_chain is None and cls._gemini_chain is None:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a structured document parser.

Your only responsibility is extracting information exactly as written.
You are not a recruiter.
You are not evaluating.
You are not summarizing.
You are not reasoning.
You are not inferring engineering knowledge.
You only normalize resume information into ResumeDataSchema.

Rules:
1. Extract ONLY information that is present in the resume text. Do not hallucinate or invent information.
2. If any field or array is missing in the text, return null or an empty array.
3. Make sure LinkedIn/GitHub/Portfolio URLs are absolute URLs (start with https:// or http://).
"""),
                ("user", """Raw Resume Text:
{resume_text}
""")
            ])

            if settings.GROQ_API_KEY:
                llm = ChatGroq(
                    api_key=SecretStr(settings.GROQ_API_KEY),
                    model="llama-3.3-70b-versatile",
                    temperature=0
                )
                cls._groq_chain = prompt | llm.with_structured_output(ResumeDataSchema)

            if settings.GEMINI_API_KEY:
                gemini_llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    api_key=SecretStr(settings.GEMINI_API_KEY),
                    temperature=0
                )
                cls._gemini_chain = prompt | gemini_llm.with_structured_output(ResumeDataSchema)

        return cls._groq_chain, cls._gemini_chain

    @staticmethod
    async def parse_resume_text(resume_text: str) -> ResumeDataSchema:
        """
        Parses raw resume text into structured Candidate Resume Schema using LLM.
        """
        if not settings.GROQ_API_KEY and not settings.GEMINI_API_KEY:
            raise RuntimeError("LLM unavailable: No AI API Keys configured in .env")

        groq_chain, gemini_chain = ResumeParserService._get_chains()
        payload_vars = {"resume_text": resume_text}

        llm_result = None
        last_error = None

        # Attempt 1: Groq
        if groq_chain:
            try:
                llm_result = await groq_chain.ainvoke(payload_vars)
            except OutputParserException as e:
                last_error = f"Invalid structured response from Groq: {str(e)}"
                logger.warning(last_error)
            except ValidationError as e:
                last_error = f"Validation failure from Groq output: {str(e)}"
                logger.warning(last_error)
            except TimeoutError:
                last_error = "Timeout while calling Groq."
                logger.warning(last_error)
            except Exception as e:
                last_error = f"Groq unavailable or failed: {str(e)}"
                logger.warning(last_error)

        # Attempt 2: Gemini
        if not llm_result and gemini_chain:
            try:
                llm_result = await gemini_chain.ainvoke(payload_vars)
            except OutputParserException as e:
                last_error = f"Invalid structured response from Gemini: {str(e)}"
                logger.warning(last_error)
            except ValidationError as e:
                last_error = f"Validation failure from Gemini output: {str(e)}"
                logger.warning(last_error)
            except TimeoutError:
                last_error = "Timeout while calling Gemini."
                logger.warning(last_error)
            except Exception as e:
                last_error = f"Gemini unavailable or failed: {str(e)}"
                logger.warning(last_error)

        if not llm_result:
            raise ValueError(f"Resume parsing failed. Last error: {last_error}")

        llm_result = cast(ResumeDataSchema, llm_result)
        ResumeParserService._sanitize_urls(llm_result)

        return llm_result

    @staticmethod
    def _sanitize_urls(data: ResumeDataSchema):
        """
        Ensures absolute URLs for standard contact fields on the constructed Pydantic object.
        """
        if not data.contact_info:
            return

        url_fields = ["linkedin_url", "github_url", "portfolio_url"]
        for field in url_fields:
            val = getattr(data.contact_info, field, None)
            if val and isinstance(val, str):
                val = val.strip()
                if val.lower() in ["none", "null", ""]:
                    setattr(data.contact_info, field, None)
                    continue
                if not val.startswith("http://") and not val.startswith("https://"):
                    setattr(data.contact_info, field, f"https://{val}")
