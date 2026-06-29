import logging
import traceback
from typing import cast, Optional
from pydantic import SecretStr
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from app.core.config import settings
from app.schemas.evidence import (
    CandidateSynthesisInput, 
    CandidateIdentity,
    EngineeringDomain,
    EngineeringCapability
)

logger = logging.getLogger(__name__)

class CandidateSynthesizerService:
    """
    Semantic reasoning layer responsible for holistically synthesizing the processed 
    engineering knowledge graph and intelligence arrays into a unified engineering identity.
    """
    
    _groq_chain = None
    _gemini_chain = None
    
    @classmethod
    def _get_chains(cls):
        if cls._groq_chain is None and cls._gemini_chain is None:
            # Generate domain list and capability list dynamically for the prompt
            domains_list = ", ".join([f'"{d.value}"' for d in EngineeringDomain])
            caps_list = ", ".join([f'"{c.value}"' for c in EngineeringCapability])

            system_prompt = f"""You are a Principal Engineering Recruiter.
You are NOT extracting raw information or parsing resumes.
You are NOT evaluating evidence quality or scoring skills.

Your responsibility is to synthesize the supplied CandidateSynthesisInput (UnifiedKnowledge, Evidence Report, Project Intelligence, Experience Intelligence, Education, Certifications) into ONE holistic, high-level CandidateIdentity.

## Grounding & Explainability Constraints:
- Every single specialization, stack technology, domain, capability, and recruiter summary statement must be groundable in the supplied evidence. Do NOT invent/hallucinate capabilities or technologies.
- Do NOT underestimate or overestimate the candidate. Use conservative conclusions based on facts.
- Produce `knowledge_reasoning` (a list of strings) that explicitly explains why you categorized the candidate's specialization, domains, and capabilities the way you did.

## Banned Content:
- Do NOT invent or add any technologies that are not explicitly present in the input.
- Do NOT calculate confidence scores or rank evidence.

## Enum Constraints (CRITICAL):
- You MUST populate `engineering_domains` ONLY with values from this exact list: [{domains_list}]
- You MUST populate `strongest_capabilities` ONLY with values from this exact list: [{caps_list}]
- If any domain or capability is not a 100% clean fit, leave it out. Never output a string that is not in the lists above.

## Styling Rules:
- The `recruiter_summary` must be written in professional, concise recruiter style.
- State: What they built, How they built it, and Why it matters technically.
- Maximum 2 sentences. No fluffy marketing words (e.g. "This project showcases...", "This candidate demonstrates...").
"""

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "Here is the structured candidate intelligence payload:\n\n{input_json}")
            ])

            if settings.GROQ_API_KEY:
                llm = ChatGroq(
                    api_key=SecretStr(settings.GROQ_API_KEY),
                    model="llama-3.3-70b-versatile",
                    temperature=0
                )
                cls._groq_chain = prompt | llm.with_structured_output(CandidateIdentity)

            if settings.GEMINI_API_KEY:
                gemini_llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    api_key=SecretStr(settings.GEMINI_API_KEY),
                    temperature=0
                )
                cls._gemini_chain = prompt | gemini_llm.with_structured_output(CandidateIdentity)
            
        return cls._groq_chain, cls._gemini_chain

    async def synthesize(self, synthesis_input: CandidateSynthesisInput) -> CandidateIdentity:
        logger.info("Starting candidate identity synthesis...")
        
        # Serialize the input to JSON for the LLM
        input_json = synthesis_input.model_dump_json(exclude_none=True, indent=2)
        payload_vars = {"input_json": input_json}
        
        groq_chain, gemini_chain = self._get_chains()
        llm_result = None
        last_error = None

        # Attempt 1: Groq
        if groq_chain:
            try:
                llm_result = await groq_chain.ainvoke(payload_vars)
                logger.info("Groq synthesis successful.")
            except Exception as e:
                last_error = e
                logger.warning(f"Groq synthesis failed: {e}. Attempting Gemini fallback...")

        # Attempt 2: Gemini
        if not llm_result and gemini_chain:
            try:
                llm_result = await gemini_chain.ainvoke(payload_vars)
                logger.info("Gemini synthesis successful.")
            except Exception as e:
                last_error = e
                logger.warning(f"Gemini synthesis failed: {e}.")

        if llm_result:
            return cast(CandidateIdentity, llm_result)

        # Both failed: log complete traceback and raise/fallback
        logger.error("All LLMs failed to synthesize candidate identity.")
        if last_error:
            logger.exception(last_error)
            logger.error(traceback.format_exc())

        # Fallback to prevent crash, but strictly log that we hit it
        logger.error("Synthesizer falling back to default 'Unknown Engineer' profile.")
        return CandidateIdentity(
            primary_specialization="Unknown Engineer",
            secondary_specializations=[],
            engineering_domains=[],
            strongest_capabilities=[],
            primary_technology_stack=[],
            supporting_technologies=[],
            engineering_profile="Failed to synthesize profile due to internal error.",
            ideal_roles=[],
            preferred_industries=[],
            recruiter_summary="Synthesis failed due to an internal error.",
            knowledge_reasoning=["Synthesis failed. Check application logs for complete traceback."]
        )
