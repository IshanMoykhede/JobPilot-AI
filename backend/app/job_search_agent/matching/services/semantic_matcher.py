import logging
from typing import List, Dict, Any
from app.vector_store.services.vector_store_service import VectorStoreService
from app.vector_store.core import vector_store_config

logger = logging.getLogger(__name__)

class SemanticMatcher:
    @staticmethod
    def compare(candidate_vector: List[float], limit: int = 100, job_search_result_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Query vector database collections using cosine similarity.
        Optionally filter by a list of job_search_result_ids (used for workspace isolation).
        Returns: List[Dict[str, Any]] containing: [{"id": str, "score": float, "payload": Dict}]
        """
        logger.info(f"[SemanticMatcher] Querying Qdrant index limit={limit}")
        collection = vector_store_config.JOB_COLLECTION
        
        filter_dict = None
        if job_search_result_ids is not None:
            filter_dict = {"job_search_result_id": job_search_result_ids}
            logger.info(f"[SemanticMatcher] Applying native payload filter for {len(job_search_result_ids)} job search result IDs")
            
        matches = VectorStoreService.search(
            collection_name=collection,
            query_vector=candidate_vector,
            limit=limit,
            filter_dict=filter_dict
        )
        logger.info(f"[SemanticMatcher] Search complete. Retrieved {len(matches)} raw matches.")
        return matches
