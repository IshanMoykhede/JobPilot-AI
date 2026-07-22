from typing import TypedDict, Optional
from uuid import UUID
from app.job_search_agent.schemas.job_knowledge import JobKnowledge
from app.job_search_agent.schemas.query_optimizer import OptimizedQuery

class JobSearchState(TypedDict):
    # UUIDs for DB reference
    job_search_id: Optional[str]
    candidate_profile_id: Optional[str]

    # Input
    user_query: str

    # Query Optimizer
    optimized_query: Optional[OptimizedQuery]

    # Job Retrieval
    raw_jobs: Optional[list[dict]]

    # Knowledge Extraction
    structured_jobs: Optional[list[dict]]

    # Candidate
    candidate_knowledge: Optional[str]

    # Matching
    matched_jobs: Optional[list[dict]]

    # Final Answer
    final_response: Optional[str]
