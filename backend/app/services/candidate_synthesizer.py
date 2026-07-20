import logging
import traceback
from typing import cast, Optional
from app.core.llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate


from app.core.config import settings
from app.schemas.evidence import (
    CandidateSynthesisInput, 
    CandidateIdentity,
    EngineeringDomain
)

logger = logging.getLogger(__name__)

class CandidateSynthesizerService:
    """
    Semantic reasoning layer responsible for holistically synthesizing the processed 
    engineering knowledge graph and intelligence arrays into a unified engineering identity.
    """
    
    _groq_chain = None
    _groq_chain = None
    
    @classmethod
    def _get_chains(cls):
        if cls._groq_chain is None:
            # Generate domain list dynamically for the prompt
            domains_list = ", ".join([f'"{d.value}"' for d in EngineeringDomain])

            system_prompt = f"""## ROLE
You are the Candidate Identity Synthesis Engine.

Your responsibility is to synthesize a candidate's complete engineering identity from structured engineering intelligence.
Choose from these engineering domains when applicable: {domains_list}

Identify:
- `primary_specialization`: The core engineering role that best represents the candidate (e.g. "Backend Developer", "ML Engineer", "Mechanical Design Engineer").
- `secondary_specializations`: List of supporting specializations (e.g. ["Cloud Engineer", "DevOps Engineer"]).
- `engineering_domains`: List of matching engineering domains from {domains_list}.
- `technology_stack`: Comprehensive, exhaustive list of ALL unique technologies, programming languages, databases, cloud providers, and frameworks the candidate knows, ensuring absolutely zero technical skills are dropped from their input projects and skills list.
- `strongest_capabilities`: List of strongest engineering capabilities (e.g. Backend Development, REST API Design, CAD Modeling).
- `experience_level`: The general seniority level (e.g., "Fresher", "Junior", "Mid-Level", "Senior").
- `ideal_roles`: List of ideal standard job titles the candidate is qualified for.

## Strict Rules
- Never invent information not present in the input.
- Return ONLY the CandidateIdentity JSON object.
"""

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "Here is the structured candidate intelligence payload:\n\n{input_json}")
            ])

            if settings.GROQ_API_KEY:
                llm = get_llm(
                    provider="groq",
                    model="llama-3.3-70b-versatile",
                    temperature=0,
                    max_tokens=8192
                )
                cls._groq_chain = prompt | llm.with_structured_output(CandidateIdentity)
            
        return cls._groq_chain

    async def synthesize(self, synthesis_input: CandidateSynthesisInput) -> CandidateIdentity:
        logger.info("Starting candidate identity synthesis...")
        print(f"\n[{'='*50}]")
        print("--> ENTERING STAGE: CANDIDATE IDENTITY SYNTHESIS")
        print("--> Input Synthesis Data:")
        print(synthesis_input.model_dump_json(indent=2))
        
        # Serialize the input to JSON for the LLM
        input_json = synthesis_input.model_dump_json(exclude_none=True, indent=2)
        payload_vars = {"input_json": input_json}
        
        groq_chain = self._get_chains()
        llm_result = None
        last_error = None

        # Attempt 1: Groq
        if groq_chain:
            try:
                from tenacity import retry, stop_after_attempt, wait_incrementing
                
                @retry(stop=stop_after_attempt(6), wait=wait_incrementing(start=15, increment=15, max=75), reraise=True)
                async def _invoke_groq():
                    return await groq_chain.ainvoke(payload_vars)
                    
                llm_result = await _invoke_groq()
                logger.info("Groq synthesis successful.")
            except Exception as e:
                last_error = e
                logger.warning(f"Groq synthesis failed: {e}.")

        if llm_result:
            print("--> Output Synthesized Candidate Identity:")
            print(llm_result.model_dump_json(indent=2))
            print(f"[{'='*50}]\n")
            return cast(CandidateIdentity, llm_result)

        # Both failed: log complete traceback and raise/fallback
        logger.error("All LLMs failed to synthesize candidate identity.")
        if last_error:
            logger.exception(last_error)
            logger.error(traceback.format_exc())

        # Fallback to prevent crash, but strictly log that we hit it
        logger.error("Synthesizer falling back to default 'Unknown Engineer' profile.")
        fallback = CandidateIdentity(
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
        print("--> Output Synthesized Candidate Identity (FALLBACK):")
        print(fallback.model_dump_json(indent=2))
        print(f"[{'='*50}]\n")
        return fallback
