from app.job_search_agent.state import JobSearchState
from app.job_search_agent.services.llm_service import optimize_query
from app.core.database import SessionLocal
from app.job_search_agent.models.job_searches import JobSearch
from app.job_search_agent.utils.logger import agent_logger

def query_optimizer_node(state: JobSearchState):
    """
    Converts the user's natural language query into a structured
    SERP-friendly search query.
    """
    user_query = state['user_query']

    agent_logger.info("=== [NODE 1] START: query_optimizer_node ===")
    agent_logger.debug(f"Input User Query: '{user_query}'")

    print(f"Optimizing query: {user_query}")
    response = optimize_query(user_query)
    
    agent_logger.debug(f"LLM Response: Job Role = '{response.job_role}', Location = '{response.location}'")

    # Optional: Update the database with the optimized query
    job_search_id = state.get("job_search_id")
    if job_search_id:
        db = SessionLocal()
        try:
            job_search = db.query(JobSearch).filter(JobSearch.id == job_search_id).first()
            if job_search:
                job_search.optimized_role = response.job_role
                job_search.optimized_location = response.location
                db.commit()
        except Exception as e:
            print(f"Error updating DB: {e}")
            agent_logger.error(f"Failed to update JobSearch DB record: {e}")
        finally:
            db.close()

    agent_logger.info("=== [NODE 1] END: query_optimizer_node ===")
    return {
        "optimized_query": response
    }
