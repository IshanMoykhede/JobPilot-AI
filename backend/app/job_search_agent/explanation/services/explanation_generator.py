import logging
from typing import List, Optional
from app.core.llm_factory import get_llm
from pydantic import SecretStr

from app.core.config import settings
from app.job_search_agent.explanation.core import explanation_config
from app.job_search_agent.explanation.core.explanation_constants import FALLBACK_SUMMARY, FALLBACK_RECOMMENDATION
from app.job_search_agent.explanation.schemas.explanation import JobExplanation, BatchJobExplanation

logger = logging.getLogger(__name__)

class ExplanationGenerator:
    @staticmethod
    async def generate(prompt: str, job_ids: List[str], match_scores: List[float]) -> List[JobExplanation]:
        """
        Invokes Gemini with structured output, retries once on failure,
        returns fallback explanations on second failure.
        """
        max_retries = explanation_config.EXPLANATION_MAX_RETRIES

        if settings.GEMINI_API_KEY:
            attempt = 0
            while True:
                try:
                    logger.info(f"[ExplanationGenerator] Attempt {attempt + 1}: calling {explanation_config.EXPLANATION_MODEL}")
                    llm = get_llm(
                        model=explanation_config.EXPLANATION_MODEL,
                        api_key=SecretStr(settings.GEMINI_API_KEY),
                        temperature=explanation_config.EXPLANATION_TEMPERATURE
                    )
                    structured_llm = llm.with_structured_output(BatchJobExplanation)
                    response = await structured_llm.ainvoke(prompt)
                    logger.info(f"[ExplanationGenerator] Received {len(response.explanations)} explanations from LLM.")
                    return response.explanations
                except Exception as e:
                    err_str = str(e).lower()
                    if "429" in err_str or "resource_exhausted" in err_str:
                        import asyncio
                        sleep_times = [10, 20, 40, 80, 160]
                        delay = sleep_times[attempt] if attempt < len(sleep_times) else 300
                        logger.warning(f"[ExplanationGenerator] 429 Rate Limit. Retrying attempt {attempt + 2} in {delay}s...")
                        await asyncio.sleep(delay)
                        attempt += 1
                        continue
                    else:
                        logger.error(f"[ExplanationGenerator] Attempt {attempt + 1} failed with non-retryable error: {e}")
                        if attempt < max_retries:
                            logger.info("[ExplanationGenerator] Retrying...")
                            attempt += 1
                            continue
                        else:
                            logger.error("[ExplanationGenerator] All retries exhausted.")
                            raise RuntimeError("Explanation Generation Failed: LLM All retries exhausted.")
        else:
            raise RuntimeError("No GEMINI_API_KEY set. Cannot generate explanations.")

    @staticmethod
    def _build_fallbacks(job_ids: List[str], match_scores: List[float]) -> List[JobExplanation]:
        """
        Generates graceful fallback explanations when the LLM is unavailable.
        """
        fallbacks = []
        for jid, score in zip(job_ids, match_scores):
            fallbacks.append(JobExplanation(
                job_id=jid,
                summary=FALLBACK_SUMMARY,
                recommendation=FALLBACK_RECOMMENDATION,
                confidence="Medium",
                reasoning="Fallback explanation generated because the AI model was unavailable."
            ))
        return fallbacks
