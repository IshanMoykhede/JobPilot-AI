import math
import logging
from typing import List, Dict, Any, Optional
from app.vector_store.providers.base_vector_store import BaseVectorStore

logger = logging.getLogger(__name__)

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if len(v1) != len(v2) or not v1:
        return 0.0
    dot_product = sum(x * y for x, y in zip(v1, v2))
    norm_a = math.sqrt(sum(x * x for x in v1))
    norm_b = math.sqrt(sum(x * x for x in v2))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

class MockVectorStore(BaseVectorStore):
    def __init__(self):
        # Format: {collection_name: {point_id: {"id": str, "vector": List[float], "payload": Dict}}}
        self._db: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def exists(self, collection_name: str, doc_hash: str) -> bool:
        collection = self._db.setdefault(collection_name, {})
        for pt in collection.values():
            if pt.get("payload", {}).get("semantic_document_hash") == doc_hash:
                return True
        return False

    def upsert(self, collection_name: str, point_id: str, vector: List[float], payload: Dict[str, Any]) -> None:
        collection = self._db.setdefault(collection_name, {})
        collection[point_id] = {
            "id": point_id,
            "vector": vector,
            "payload": payload
        }
        logger.info(f"[MockVectorStore] Upserted point {point_id} to collection {collection_name}")

    def upsert_batch(self, collection_name: str, points: List[Dict[str, Any]]) -> None:
        collection = self._db.setdefault(collection_name, {})
        for pt in points:
            pid = pt["id"]
            collection[pid] = pt
        logger.info(f"[MockVectorStore] Upserted batch of {len(points)} points to collection {collection_name}")

    def search(self, collection_name: str, query_vector: List[float], limit: int = 100) -> List[Dict[str, Any]]:
        collection = self._db.setdefault(collection_name, {})
        results = []
        for pid, pt in collection.items():
            sim = cosine_similarity(query_vector, pt["vector"])
            results.append({
                "id": pid,
                "score": sim,
                "payload": pt["payload"]
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def get(self, collection_name: str, filter_field: str, filter_value: str) -> Optional[Dict[str, Any]]:
        collection = self._db.setdefault(collection_name, {})
        for pt in collection.values():
            if str(pt.get("payload", {}).get(filter_field)) == str(filter_value):
                return pt
        return None
