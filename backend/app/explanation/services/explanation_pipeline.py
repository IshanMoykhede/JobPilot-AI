import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.explanation.core import explanation_config
from app.explanation.schemas.explanation import JobExplanation
from app.explanation.services.prompt_builder import PromptBuilder
from app.explanation.services.explanation_generator import ExplanationGenerator

from app.matching.schemas.matching_result import RankedJob
from app.job_search.models.job_knowledge import JobKnowledge
from app.job_search.models.job_search_result import JobSearchResult
from app.conversation.models.conversation_message import ConversationMessage, Role, MessageType

logger = logging.getLogger(__name__)

class ExplanationPipeline:
    @staticmethod
    async def run(
        db: Session,
        ranked_jobs: List[RankedJob],
        conversation_id: Optional[uuid.UUID] = None
    ) -> List[JobExplanation]:
        """
        Orchestrates Candidate Guidance generation:
        1. Select top N jobs
        2. Load corresponding JobKnowledge records (MatchKnowledge context)
        3. Process in configurable batches
        4. Calculate deterministic application decision and confidence
        5. Persist as conversation message for replay
        6. Return structured candidate guidance
        """
        top_n = explanation_config.TOP_JOBS_TO_EXPLAIN
        batch_size = explanation_config.EXPLANATION_BATCH_SIZE

        # 1. Select top N
        top_jobs = ranked_jobs[:top_n]
        logger.info(f"[ExplanationPipeline] Generating Candidate Guidance for top {len(top_jobs)} of {len(ranked_jobs)} jobs.")

        if not top_jobs:
            logger.info("[ExplanationPipeline] No ranked jobs to process.")
            return []

        # 2. Load JobSearchResult records directly
        job_result_ids = [rj.job_search_result_id for rj in top_jobs]
        results = db.query(JobSearchResult).filter(JobSearchResult.id.in_(job_result_ids)).all()
        res_map = {res.id: res for res in results}

        # Build job entries with comparison_evidence
        job_entries = []
        for rj in top_jobs:
            res = res_map.get(rj.job_search_result_id)
            if res and res.comparison_evidence:
                job_entries.append({
                    "job_title": res.job_title,
                    "company_name": res.company_name or "Unknown Company",
                    "comparison_evidence": res.comparison_evidence,
                    "match_score": rj.final_match_score,
                    "job_search_result_id": str(rj.job_search_result_id)
                })
            else:
                logger.warning(f"[ExplanationPipeline] comparison_evidence not found for result {rj.job_search_result_id}. Skipping.")

        if not job_entries:
            logger.info("[ExplanationPipeline] No valid job entries to guide on.")
            return []

        # 3. Process in batches concurrently with Semaphore
        import asyncio
        from app.explanation.schemas.explanation import ApplicationDecision, ActionItem, ActionPriority
        
        all_explanations: List[JobExplanation] = []
        semaphore = asyncio.Semaphore(5)

        def _calculate_deterministic_fields(match_score: float) -> tuple:
            if match_score >= 85:
                return "High", ApplicationDecision.STRONG_APPLY
            elif match_score >= 70:
                return "Medium", ApplicationDecision.APPLY
            elif match_score >= 50:
                return "Medium", ApplicationDecision.STRETCH_APPLY
            else:
                return "Low", ApplicationDecision.NOT_RECOMMENDED

        async def _process_explanation_batch(batch_num: int, batch: List[Dict[str, Any]]) -> List[JobExplanation]:
            async with semaphore:
                logger.info(f"[ExplanationPipeline] Processing guidance batch {batch_num} ({len(batch)} jobs)")
                try:
                    # Pass the batch exactly as needed. No raw candidate knowledge!
                    prompt = PromptBuilder.build_batch_prompt(batch)
                    
                    job_ids = [entry["job_search_result_id"] for entry in batch]
                    match_scores = [entry["match_score"] for entry in batch]

                    explanations_result = await ExplanationGenerator.generate(prompt, job_ids, match_scores)
                    
                    # Compute Deterministic properties and inject them
                    for exp in explanations_result:
                        # Find corresponding match score for this job ID
                        score = next((entry["match_score"] for entry in batch if entry["job_search_result_id"] == exp.job_id), 0.0)
                        conf, decision = _calculate_deterministic_fields(score)
                        exp.confidence = conf
                        exp.application_decision = decision
                        
                    return explanations_result
                except Exception as batch_err:
                    logger.error(f"[ExplanationPipeline] Batch {batch_num} failed: {batch_err}. Generating fallbacks.")
                    fallbacks = []
                    for entry in batch:
                        score = entry["match_score"]
                        conf, decision = _calculate_deterministic_fields(score)
                        
                        fallbacks.append(JobExplanation(
                            job_id=entry["job_search_result_id"],
                            overall_fit="This role aligns well with your demonstrated technologies and engineering background.",
                            strengths=["General Software Engineering Background"],
                            skill_gaps=[],
                            experience_assessment="Total experience meets baseline estimates.",
                            education_assessment="Degree status meets expectations.",
                            application_decision=decision,
                            application_reason="Fallback generated due to API disruption.",
                            resume_focus_areas=["Highlight technical accomplishments"],
                            interview_focus_areas=["Prepare for standard engineering rounds"],
                            next_steps=[ActionItem(priority=ActionPriority.MEDIUM, action="Review the job description.")],
                            confidence=conf
                        ))
                    return fallbacks

        tasks = []
        for i in range(0, len(job_entries), batch_size):
            batch = job_entries[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            tasks.append(_process_explanation_batch(batch_num, batch))
            
        results = await asyncio.gather(*tasks)
        for res in results:
            all_explanations.extend(res)

        # 4. Persist to JobSearchResult directly and as conversation message (replay without re-generation)
        if all_explanations:
            try:
                for exp in all_explanations:
                    # Convert exp.job_id string to UUID safely
                    job_uuid = uuid.UUID(exp.job_id) if isinstance(exp.job_id, str) else exp.job_id
                    db_res = db.query(JobSearchResult).filter(JobSearchResult.id == job_uuid).first()
                    if db_res:
                        db_res.ai_explanation = exp.model_dump()
                db.commit()
                logger.info(f"[ExplanationPipeline] Persisted AI explanations directly to {len(all_explanations)} JobSearchResult records.")
            except Exception as db_err:
                db.rollback()
                logger.error(f"[ExplanationPipeline] Failed to save AI explanations to JobSearchResult: {db_err}")

        if conversation_id and all_explanations:
            try:
                message_content = {
                    "type": "job_explanations",
                    "explanations": [exp.model_dump() for exp in all_explanations],
                    "generated_at": datetime.now(timezone.utc).isoformat()
                }
                msg = ConversationMessage(
                    conversation_id=conversation_id,
                    role=Role.ASSISTANT,
                    message_type=MessageType.JOB_RESULTS,
                    content=message_content,
                    message_metadata={"explanation_count": len(all_explanations)}
                )
                db.add(msg)
                db.commit()
                logger.info(f"[ExplanationPipeline] Persisted {len(all_explanations)} explanations to conversation {conversation_id}.")
            except Exception as persist_err:
                db.rollback()
                logger.error(f"[ExplanationPipeline] Failed to persist conversation message: {persist_err}")

        logger.info(f"[ExplanationPipeline] Pipeline complete. Total explanations: {len(all_explanations)}")
        return all_explanations
