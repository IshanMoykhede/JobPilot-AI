import random
from app.job_search_agent.state import JobSearchState
from app.core.database import SessionLocal
from app.job_search_agent.models.job_match_scores import JobMatchScore
from app.job_search_agent.models.job_knowledge import JobKnowledge as JobKnowledgeModel
from app.job_search_agent.utils.logger import agent_logger

def scorer_node(state: JobSearchState):
    """
    Temporary MVP node to assign random scores to matched jobs
    and persist them to the job_match_scores table.
    """
    agent_logger.info("=== [NODE 6] START: scorer_node ===")
    
    matched_jobs = state.get("matched_jobs", [])
    job_search_id = state.get("job_search_id")
    
    if not matched_jobs or not job_search_id:
        agent_logger.warning("Missing matched_jobs or job_search_id in state, skipping scoring.")
        agent_logger.info("=== [NODE 6] END: scorer_node ===")
        return {}

    db = SessionLocal()
    try:
        print(f"Scoring {len(matched_jobs)} matched jobs...")
        agent_logger.debug(f"Assigning scores for {len(matched_jobs)} jobs under search ID: {job_search_id}...")
        
        for job in matched_jobs:
            # Generate fake scores
            semantic_score = random.uniform(60.0, 95.0)
            deterministic_score = random.uniform(50.0, 99.0)
            final_score = (semantic_score + deterministic_score) / 2.0
            
            # Try to find the job_knowledge_id in DB (we saved it earlier based on hash)
            import hashlib
            stable_id_str = f"{job.job_title}_{job.company_name}".lower().encode('utf-8')
            job_hash = hashlib.md5(stable_id_str).hexdigest()
            
            db_job = db.query(JobKnowledgeModel).filter(JobKnowledgeModel.job_hash == job_hash).first()
            if db_job:
                # Save to job_match_scores
                score_record = JobMatchScore(
                    job_search_id=job_search_id,
                    job_knowledge_id=db_job.id,
                    semantic_score=semantic_score,
                    deterministic_score=deterministic_score,
                    final_score=final_score,
                    matching_skills=["Python", "SQL"] if final_score > 80 else [],
                    missing_skills=["Docker"] if final_score < 70 else []
                )
                db.add(score_record)
        
        db.commit()
        print("Scores saved to database successfully.")
        agent_logger.debug("Successfully saved all scores to job_match_scores table.")
        
    except Exception as e:
        print(f"Error in scorer node: {e}")
        agent_logger.error(f"Error in scorer node: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

    agent_logger.info("=== [NODE 6] END: scorer_node ===")
    return {}
