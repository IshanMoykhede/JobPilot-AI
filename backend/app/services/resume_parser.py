import logging
from pydantic import ValidationError

from app.core.llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.exceptions import OutputParserException


from app.core.config import settings
from app.schemas.candidate_profile import ResumeDataSchema
from pydantic import SecretStr
from typing import cast

logger = logging.getLogger(__name__)

class ResumeParserService:
    _groq_chain = None

    @classmethod
    def _get_chains(cls):
        """Initializes and caches LLM chains globally."""
        if cls._groq_chain is None:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """## Role
You are a high-fidelity, structured Resume Parser Engine.

## Objective
Convert raw, unstructured resume text into a structured JSON matching the `ResumeDataSchema` schema exactly. You are NOT evaluating the candidate, summarizing their history, or inferring any skills. You are a copy-paste router.

## Strict Parsing Rules

### 1. Copy-Paste Verbatim (No Shortening or Rephrasing)
- You must preserve the exact text, words, and structure of descriptions for projects (`projects.description`) and professional experiences (`experience.description`).
- **NEVER** truncate, shorten, summarize, or omit bullet points. If a project has 3 detailed bullet points under it, copy all 3 bullet points verbatim into the description. 
- You are a copy-paste extraction engine. You classify data, but you do not write, edit, correct grammar, or simplify anything.

### 2. Lossless Extraction (Zero Omissions)
- Every single piece of information, project details, job details, certifications, and skills in the raw resume must be routed to the correct field in the schema.
- If a section exists in the raw resume, it must be fully extracted. Skipping or leaving out details is a failure.

### 3. Skill Extraction and Compound Splitting
- Extract all technical skills and tools listed.
- When skills are listed as compound or combined strings (e.g., "HTML/CSS/JavaScript" or "FastAPI, Git, Docker"), split them into individual, separate strings in the array (e.g., `["HTML", "CSS", "JavaScript", "FastAPI", "Git", "Docker"]`).
- Never infer skills that are not explicitly typed.

### 4. Experience vs. Project Routing
- **Experience:** If the candidate worked for a company, organization, or institution (including internships, traineeships, or freelance contracts), route it to the `experience` list. Keep the title/role exactly as written.
- **Projects:** If the candidate built a specific tool, open-source project, or academic build (e.g., "CampusConnect", "VaultVani"), route it to the `projects` list. Ensure the title, full description (all bullet points), and technologies used are fully populated.

### 5. Education & Certifications
- Extract every single academic entry (degree, school, year) into `education`. Do not omit high school or previous degrees.
- Extract every credential or course completed into `certifications`. Ensure you capture the full certification name, issuer, year, and URLs if present.

### 6. Value Sanitization
- Ensure contact URLs (GitHub, LinkedIn, Portfolios) are absolute URLs starting with `http://` or `https://`.
- For dates, extract exactly as written (e.g., "Jan 2023", "2023", "Present"). Do not guess or invent months/days.
- If any array or field is completely missing from the resume, leave it as an empty array or `null`.

"""),
                ("user", """Raw Resume Text:
{resume_text}
""")
            ])

            if settings.GROQ_API_KEY:
                llm = get_llm(
                    provider="groq",
                    model="llama-3.3-70b-versatile",
                    temperature=0,
                    max_tokens=8192
                )
                cls._groq_chain = prompt | llm.with_structured_output(ResumeDataSchema)

        return cls._groq_chain

    @staticmethod
    async def parse_resume_text(resume_text: str) -> ResumeDataSchema:
        """
        Parses raw resume text into structured Candidate Resume Schema using LLM.
        """
        print(f"\n[{'='*50}]")
        print("--> ENTERING STAGE: RESUME PARSING")
        print("--> Input Raw Text:")
        print(resume_text[:2000] + ("..." if len(resume_text) > 2000 else ""))

        if not settings.GROQ_API_KEY:
            raise RuntimeError("LLM unavailable: No AI API Keys configured in .env")

        groq_chain = ResumeParserService._get_chains()
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

        if not llm_result:
            raise ValueError(f"Resume parsing failed. Last error: {last_error}")

        llm_result = cast(ResumeDataSchema, llm_result)
        ResumeParserService._sanitize_urls(llm_result)

        print("--> Output Parse Result:")
        print(llm_result.model_dump_json(indent=2))
        print(f"[{'='*50}]\n")

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
