from app.job_search_agent.state import JobSearchState
from app.core.database import SessionLocal
from app.job_search_agent.models.job_match_scores import JobMatchScore
from app.job_search_agent.utils.logger import agent_logger
from app.job_search_agent.services.llm_service import llm
from app.job_search_agent.schemas.scorer import JobEvaluationBatch
from app.job_search_agent.prompts.scorer_prompt import SCORER_SYSTEM_PROMPT
from langchain_core.messages import SystemMessage, HumanMessage
import json

def scorer_node(state: JobSearchState):
    """
    Evaluates the top matched jobs using an LLM to extract matching and missing skills.
    Calculates a final score mathematically and bulk inserts the results.
    """
    agent_logger.info("=== [NODE 6] START: scorer_node ===")
    
    matched_jobs = state.get("matched_jobs", [])
    job_search_id = state.get("job_search_id")
    candidate_profile_id = state.get("candidate_profile_id")
    
    if not matched_jobs or not job_search_id or not candidate_profile_id:
        agent_logger.warning("Missing required state variables for scoring, skipping.")
        agent_logger.info("=== [NODE 6] END: scorer_node ===")
        return {}

    db = SessionLocal()
    try:
        from app.models.candidate_profile import CandidateProfile # Import to fix SQLAlchemy registry
        from app.models.candidate_insights import CandidateInsights, ArtifactType, InsightStatus
        insight = db.query(CandidateInsights).filter(
            CandidateInsights.candidate_profile_id == candidate_profile_id,
            CandidateInsights.artifact_type == ArtifactType.CANDIDATE_KNOWLEDGE,
            CandidateInsights.status == InsightStatus.COMPLETED
        ).first()
        
        candidate_knowledge = insight.artifact_json if insight else {}
        if not candidate_knowledge:
            agent_logger.error("No candidate knowledge found in DB.")
            raise ValueError(f"Candidate {candidate_profile_id} has no extracted knowledge.")
    except Exception as e:
        agent_logger.error(f"Failed to fetch candidate knowledge: {e}")
        raise e
    finally:
        db.close()

    # Take the top 15 jobs to save LLM tokens
    top_jobs = matched_jobs[:15]
    
    # Format the prompt payload
    jobs_payload = []
    for job_dict in top_jobs:
        job = job_dict["job_knowledge"]
        
        # safely combine domains
        domains = []
        if job.primary_domain: domains.append(job.primary_domain)
        domains.extend(job.secondary_domains)
        
        jobs_payload.append({
            "job_id": job_dict["id"],
            "title": job.job_title,
            "employment_type": job.employment_type,
            "experience": f"Min: {job.minimum_experience_years}, Preferred: {job.preferred_experience_years}",
            "degrees": job.required_degrees + job.preferred_degrees,
            "domains": domains,
            "tech": job.required_technologies + job.preferred_technologies,
            "capabilities": job.required_capabilities + job.preferred_capabilities,
            "responsibilities": job.responsibilities
        })

    agent_logger.debug(f"Sending {len(top_jobs)} jobs to LLM for skill evaluation...")
    
    try:
        from app.job_search_agent.utils.token_batcher import create_token_batches
        from app.job_search_agent.utils.token_counter import count_tokens
        from app.embedding.services.candidate_document_builder import CandidateDocumentBuilder
        import time
        import groq
        
        structured_llm = llm.with_structured_output(JobEvaluationBatch)
        evaluations = {}
        
        # Build clean semantic candidate profile document (~400 tokens instead of 10,000+ raw JSON tokens)
        candidate_doc_text = CandidateDocumentBuilder.build_document(candidate_knowledge)
        candidate_profile_str = f"CANDIDATE PROFILE:\n{candidate_doc_text}\n\n"
        candidate_profile_tokens = count_tokens(candidate_profile_str)
        
        # Max limit per request = 8,000 tokens total
        # Budget left for jobs = 8000 - candidate_profile_tokens
        jobs_budget = 8000 - candidate_profile_tokens
        
        agent_logger.debug(
            f"Token budget: 8000 total max limit, {candidate_profile_tokens} for candidate profile, "
            f"{jobs_budget} remaining for system prompt + jobs + output"
        )
        
        batches = create_token_batches(
            jobs=jobs_payload,
            system_prompt=SCORER_SYSTEM_PROMPT,  # Only the real ~300 token system prompt
            max_context_tokens=jobs_budget,
            reserved_output_tokens=1500,
            safety_margin=500
        )
        
        agent_logger.debug(f"Created {len(batches)} scorer batches from {len(jobs_payload)} jobs.")
        
        for idx, batch_payload in enumerate(batches):
            user_content = candidate_profile_str + f"JOBS BATCH:\n{json.dumps(batch_payload, indent=2)}"
            
            messages = [
                SystemMessage(content=SCORER_SYSTEM_PROMPT),
                HumanMessage(content=user_content)
            ]
            
            # Retry loop for rate limits (Groq throws 413 or 429 for TPM limits)
            for attempt in range(4):
                try:
                    response = structured_llm.invoke(messages)
                    for eval_obj in response.evaluations:
                        evaluations[eval_obj.job_id] = eval_obj
                    agent_logger.debug(f"Scorer batch {idx + 1}/{len(batches)} completed.")
                    break
                except Exception as e:
                    error_str = str(e).lower()
                    if ("429" in error_str or "413" in error_str or "rate_limit" in error_str) and attempt < 3:
                        wait_time = 60 * (attempt + 1)
                        agent_logger.warning(f"Rate limited on scorer batch {idx + 1}. Retrying in {wait_time}s (attempt {attempt + 1}/3)...")
                        time.sleep(wait_time)
                    else:
                        raise e
            
    except Exception as e:
        agent_logger.error(f"LLM scoring failed: {e}", exc_info=True)
        raise e

    db = SessionLocal()
    try:
        score_records = []
        for job_dict in top_jobs:
            job_id = job_dict["id"]
            evaluation = evaluations.get(job_id)
            
            if evaluation:
                matching = evaluation.matching_tech + evaluation.matching_qualifications + evaluation.matching_capabilities
                missing = evaluation.missing_tech + evaluation.missing_qualifications + evaluation.missing_capabilities
                total = len(matching) + len(missing)
                final_score = (len(matching) / total * 100) if total > 0 else 50.0
            else:
                matching = []
                missing = []
                final_score = 50.0  # Fallback

            # Create bulk record
            score_record = JobMatchScore(
                job_search_id=job_search_id,
                job_knowledge_id=job_id,
                semantic_score=None,
                deterministic_score=None,
                final_score=final_score,
                matching_skills=matching,
                missing_skills=missing
            )
            score_records.append(score_record)

        if score_records:
            db.add_all(score_records)
            db.commit()
            agent_logger.debug(f"Successfully bulk inserted {len(score_records)} scores.")
            
    except Exception as e:
        print(f"Error bulk inserting scores: {e}")
        agent_logger.error(f"Error bulk inserting scores: {e}", exc_info=True)
        db.rollback()
        raise e
    finally:
        db.close()

    agent_logger.info("=== [NODE 6] END: scorer_node ===")
    return {}
