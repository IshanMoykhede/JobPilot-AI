from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional

class RankedJob(BaseModel):
    job_search_result_id: UUID
    job_title: str
    company_name: Optional[str] = None
    semantic_score: float
    final_match_score: float

class RankedJobList(BaseModel):
    workspace_id: UUID
    ranked_jobs: List[RankedJob]
