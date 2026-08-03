import logging
from typing import List
from app.job_search_agent.matching.schemas.matching_result import RankedJob

logger = logging.getLogger(__name__)

class RankingService:
    @staticmethod
    def rank_jobs(jobs: List[RankedJob]) -> List[RankedJob]:
        """
        Sorts RankedJob entries descending by final_match_score.
        """
        logger.info(f"[RankingService] Ranking {len(jobs)} jobs.")
        return sorted(jobs, key=lambda x: x.final_match_score, reverse=True)
