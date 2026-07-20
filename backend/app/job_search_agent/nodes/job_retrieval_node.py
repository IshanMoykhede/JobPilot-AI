from app.job_search_agent.state import JobSearchState
from app.job_search_agent.services.serp_api_service import search_jobs_via_serpapi
from app.job_search_agent.utils.logger import agent_logger

def job_retrieval_node(state: JobSearchState):
    """
    Fetches raw job listings from SERP API based on the optimized query.
    """
    optimized_query = state.get("optimized_query")
    agent_logger.info("=== [NODE 2] START: job_retrieval_node ===")
    
    if not optimized_query:
        agent_logger.error("Optimized query is missing from state.")
        raise ValueError("Optimized query is missing from state.")
    
    job_role = optimized_query.job_role
    location = optimized_query.location

    agent_logger.debug(f"Fetching jobs for '{job_role}' in '{location}'...")
    print(f"Fetching jobs for '{job_role}' in '{location}'...")
    
    raw_jobs = search_jobs_via_serpapi(job_role, location)
    
    print(f"Retrieved {len(raw_jobs)} raw jobs from SERP API.")
    agent_logger.info(f"Retrieved {len(raw_jobs)} raw jobs from SERP API.")
    if raw_jobs:
        agent_logger.debug(f"Sample Job 1 Title: {raw_jobs[0].get('title')}")

    agent_logger.info("=== [NODE 2] END: job_retrieval_node ===")
    return {
        "raw_jobs": raw_jobs
    }
