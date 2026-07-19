import logging
import asyncio
from typing import List
from pydantic import SecretStr

from app.core.config import settings
from app.core.llm_factory import get_llm, get_structured_llm
from app.job_search.models.job_knowledge import JobKnowledge
from app.matching.schemas.comparison import BatchLLMComparisonResult
from app.embedding.services.job_document_builder import JobDocumentBuilder

logger = logging.getLogger(__name__)

COMPARISON_PROMPT = """You are an expert Engineering Recruiter and Semantic Matcher.
Your task is to compare a Candidate's Semantic Profile against multiple structured Job Requirement profiles.

CANDIDATE SEMANTIC PROFILE (What they possess):
{candidate_profile}

JOB REQUIREMENTS TO EVALUATE:
{jobs_payload}

INSTRUCTIONS:
1. Compare the Candidate's Profile against each of the provided Job Requirements independently.
2. Evaluate technologies, capabilities, domains, education, certifications, and experience.
3. Understand semantic equivalence (e.g., "ReactJS" matches "React", "Postgres" matches "PostgreSQL").
4. For every matched or partial match, preserve the exact semantic relationship. Instead of just a list of strings, output objects containing `job_requirement`, `candidate_skill` (the exact term the candidate used), and `match_type` (e.g., 'exact', 'equivalent', 'partial').
5. Capture a complete Gap Analysis. Explicitly populate missing requirements (technologies, capabilities, certifications, degrees).
6. Make sure the `job_id` matches the provided job_id in the payload exactly.
7. Output a list of results inside the JSON matching the required schema.

Note on Experience:
Compare the candidate's total experience in months against the job's minimum and preferred years.
"""

# Create a global semaphore: Max 3 concurrent LLM calls at a time
gemini_semaphore = asyncio.Semaphore(3)

class LLMComparisonService:
    @staticmethod
    async def compare_batch(candidate_semantic_doc: str, jobs: List[JobKnowledge]) -> BatchLLMComparisonResult:
        """
        Invokes the LLM to perform a structured semantic comparison between the Candidate and a Batch of Jobs.
        """
        jobs_payload_parts = []
        for jk in jobs:
            job_doc = JobDocumentBuilder.build_document(jk)
            jobs_payload_parts.append(f"--- JOB ID: {jk.id} ---\n{job_doc}\n")
            
        jobs_payload = "\n".join(jobs_payload_parts)
        
        prompt = COMPARISON_PROMPT.format(
            candidate_profile=candidate_semantic_doc,
            jobs_payload=jobs_payload
        )
        
        async with gemini_semaphore:
            attempt = 1
            while True:
                try:
                    # Add a micro-sleep between batch executions to spread requests
                    await asyncio.sleep(2.0)
                    
                    structured_llm = get_structured_llm(BatchLLMComparisonResult)
                    
                    logger.info(f"[LLMComparisonService] Calling LLM for structured batch comparison (Batch Size: {len(jobs)}, Attempt {attempt})")
                    result = await structured_llm.ainvoke(prompt)
                    return result
                except Exception as e:
                    err_str = str(e).lower()
                    if "429" in err_str or "resource_exhausted" in err_str:
                        sleep_times = [5, 10, 20]
                        delay = sleep_times[attempt - 1] if attempt <= len(sleep_times) else 20
                        if attempt > 3:
                            logger.error(f"[LLMComparisonService] Max retries exceeded for LLM Rate Limit: {e}")
                            raise
                        logger.warning(f"[LLMComparisonService] 429 Rate Limit. Retrying in {delay}s...")
                        await asyncio.sleep(delay)
                        attempt += 1
                    else:
                        logger.error(f"[LLMComparisonService] LLM structured batch comparison failed: {e}")
                        raise
