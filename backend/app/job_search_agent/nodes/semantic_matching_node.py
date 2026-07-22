from app.job_search_agent.state import JobSearchState
from app.job_search_agent.services.qdrant_service import retrieve_candidate_embedding, search_similar_jobs
from app.job_search_agent.utils.logger import agent_logger

def semantic_matching_node(state: JobSearchState):
    """
    Retrieves the candidate's embedding from Qdrant, searches for semantically 
    similar jobs, and updates the state with the matched jobs.
    """
    agent_logger.info("=== [NODE 5] START: semantic_matching_node ===")
    
    candidate_profile_id = state.get("candidate_profile_id")
    
    if not candidate_profile_id:
        print("No candidate_profile_id provided, skipping semantic matching.")
        agent_logger.warning("No candidate_profile_id provided, skipping semantic matching.")
        agent_logger.info("=== [NODE 5] END: semantic_matching_node ===")
        return {"matched_jobs": state.get("structured_jobs", [])}
        
    print(f"\nFetching embedding for Candidate Profile ID {candidate_profile_id}...")
    agent_logger.debug(f"Fetching embedding for Candidate Profile ID {candidate_profile_id}...")
    try:
        candidate_embedding = retrieve_candidate_embedding(candidate_id=candidate_profile_id)
        
        print("Searching for semantically similar jobs in Qdrant...")
        # Get top 50 matches to allow all retrieved jobs to be scored
        matched_jobs = search_similar_jobs(
            candidate_embedding=candidate_embedding,
            conversation_id=state.get("job_search_id"),
            limit=50
        )
        
        print(f"Found {len(matched_jobs)} matching jobs!")
        agent_logger.debug(f"Found {len(matched_jobs)} semantically similar jobs.")

        agent_logger.info("=== [NODE 5] END: semantic_matching_node ===")
        return {
            "matched_jobs": matched_jobs
        }
    except Exception as e:
        print(f"Failed to fetch candidate embeddings or perform search: {e}")
        agent_logger.error(f"Failed to fetch candidate embeddings or perform search: {e}", exc_info=True)
        raise e
