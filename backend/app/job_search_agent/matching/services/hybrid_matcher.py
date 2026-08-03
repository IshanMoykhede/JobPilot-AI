import logging
from app.job_search_agent.matching.core import matching_config

logger = logging.getLogger(__name__)

class HybridMatcher:
    @staticmethod
    def calculate_hybrid_score(semantic_score: float, deterministic_score: float) -> float:
        """
        Combines semantic similarity (normalized to 0-100) with deterministic score.
        """
        # Normalize cosine similarity (usually 0.0 to 1.0) to 0.0 to 100.0 range
        normalized_semantic = max(0.0, semantic_score) * 100.0
        
        sw = matching_config.SEMANTIC_WEIGHT
        dw = matching_config.DETERMINISTIC_WEIGHT
        
        hybrid = (normalized_semantic * sw) + (deterministic_score * dw)
        logger.info(f"[HybridMatcher] Blended score: semantic={normalized_semantic:.1f}, deterministic={deterministic_score:.1f} -> hybrid={hybrid:.2f}")
        return min(100.0, max(0.0, hybrid))
