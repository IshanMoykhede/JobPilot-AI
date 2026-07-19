import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient  # type: ignore
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue  # type: ignore

from app.vector_store.providers.base_vector_store import BaseVectorStore
from app.vector_store.core import vector_store_config

logger = logging.getLogger(__name__)

class QdrantProvider(BaseVectorStore):
    def __init__(self, url: str, api_key: Optional[str] = None, dimension: int = 384):
        self.url = url
        self.api_key = api_key
        self.dimension = dimension
        try:
            self.client = QdrantClient(url=url, api_key=api_key, timeout=30.0)
            # Perform query to verify actual network connectivity
            self.client.get_collections()
            self._ensure_collection(vector_store_config.CANDIDATE_COLLECTION)
            self._ensure_collection(vector_store_config.JOB_COLLECTION)
        except Exception as e:
            logger.error(f"[QdrantProvider] Failed to connect to Qdrant at {url}: {e}. QdrantProvider degraded.")
            raise e

    def _ensure_collection(self, collection_name: str) -> None:
        try:
            if not self.client.collection_exists(collection_name):
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE)
                )
                logger.info(f"[QdrantProvider] Collection '{collection_name}' created.")
            else:
                logger.info(f"[QdrantProvider] Collection '{collection_name}' already exists.")

            # ALWAYS ensure payload indexes, independently of collection creation
            self._ensure_payload_indexes(collection_name)
        except Exception as e:
            logger.warning(f"[QdrantProvider] Error checking/creating collection '{collection_name}': {e}")

    def _ensure_payload_indexes(self, collection_name: str) -> None:
        logger.info(f"[QdrantProvider] Ensuring payload indexes for '{collection_name}'...")
        from qdrant_client.models import PayloadSchemaType
        
        indexes_to_create = []
        if collection_name == vector_store_config.JOB_COLLECTION:
            indexes_to_create = [
                "job_search_result_id",
                "workspace_id",
                "job_knowledge_id",
                "semantic_document_hash"
            ]
        elif collection_name == vector_store_config.CANDIDATE_COLLECTION:
            indexes_to_create = [
                "candidate_knowledge_id",
                "semantic_document_hash"
            ]
            
        try:
            collection_info = self.client.get_collection(collection_name)
            existing_indexes = collection_info.payload_schema.keys() if collection_info.payload_schema else []
        except Exception as e:
            logger.error(f"[QdrantProvider] Failed to fetch collection info for '{collection_name}': {e}")
            raise e
            
        for index_name in indexes_to_create:
            if index_name in existing_indexes:
                logger.info(f"[QdrantProvider] Payload index verified (already exists): {index_name}")
                continue

            try:
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name=index_name,
                    field_schema=PayloadSchemaType.KEYWORD
                )
                logger.info(f"[QdrantProvider] Payload index verified: {index_name}")
            except Exception as e:
                logger.error(f"[QdrantProvider] Error ensuring payload index '{index_name}': {e}")
                raise e

        try:
            final_info = self.client.get_collection(collection_name)
            final_indexes = list(final_info.payload_schema.keys()) if final_info.payload_schema else []
            
            log_lines = [f"Collection : {collection_name}", "Payload indexes:"]
            for idx in final_indexes:
                log_lines.append(f"✓ {idx}")
                
            logger.info("[QdrantProvider] Final Payload Schema:\n" + "\n".join(log_lines))
        except Exception as e:
            logger.error(f"[QdrantProvider] Failed to fetch final collection info for logging: {e}")

    def exists(self, collection_name: str, doc_hash: str) -> bool:
        try:
            res = self.client.scroll(
                collection_name=collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="semantic_document_hash",
                            match=MatchValue(value=doc_hash)
                        )
                    ]
                ),
                limit=1
            )
            return len(res[0]) > 0
        except Exception as e:
            logger.error(f"[QdrantProvider] Error checking existence in Qdrant: {e}")
            raise e

    def _sanitize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures ID fields are stored as strings to match KEYWORD indexes."""
        sanitized = payload.copy()
        id_fields = [
            "job_search_result_id", 
            "workspace_id", 
            "candidate_knowledge_id", 
            "job_knowledge_id"
        ]
        for field in id_fields:
            if field in sanitized and sanitized[field] is not None:
                sanitized[field] = str(sanitized[field])
        return sanitized

    def upsert(self, collection_name: str, point_id: str, vector: List[float], payload: Dict[str, Any]) -> None:
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=self._sanitize_payload(payload)
                    )
                ]
            )
            logger.info(f"[QdrantProvider] Upserted {point_id} in Qdrant collection {collection_name}")
        except Exception as e:
            logger.error(f"[QdrantProvider] Failed to upsert to Qdrant: {e}")
            raise e

    def upsert_batch(self, collection_name: str, points: List[Dict[str, Any]]) -> None:
        try:
            structs = []
            for pt in points:
                structs.append(
                    PointStruct(
                        id=pt["id"],
                        vector=pt["vector"],
                        payload=self._sanitize_payload(pt["payload"])
                    )
                )
            self.client.upsert(
                collection_name=collection_name,
                points=structs
            )
            logger.info(f"[QdrantProvider] Upserted batch of {len(points)} to collection {collection_name}")
        except Exception as e:
            logger.error(f"[QdrantProvider] Failed batch upsert to Qdrant: {e}")
            raise e

    def search(self, collection_name: str, query_vector: List[float], limit: int = 100, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchAny
            qdrant_filter = None
            if filter_dict:
                must_conditions = []
                for key, values in filter_dict.items():
                    if isinstance(values, list):
                        must_conditions.append(FieldCondition(key=key, match=MatchAny(any=values)))
                    else:
                        from qdrant_client.models import MatchValue
                        must_conditions.append(FieldCondition(key=key, match=MatchValue(value=values)))
                if must_conditions:
                    qdrant_filter = Filter(must=must_conditions)

            res = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                query_filter=qdrant_filter,
                limit=limit
            )
            # query_points returns QueryResponse, which has .points
            results = []
            for hit in res.points:
                results.append({
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                })
            return results
        except Exception as e:
            logger.error(f"[QdrantProvider] Search failed in Qdrant collection {collection_name}: {e}")
            raise e

    def get(self, collection_name: str, filter_field: str, filter_value: str) -> Optional[Dict[str, Any]]:
        try:
            res = self.client.scroll(
                collection_name=collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key=filter_field,
                            match=MatchValue(value=filter_value)
                        )
                    ]
                ),
                limit=1,
                with_vectors=True
            )
            if res[0]:
                hit = res[0][0]
                return {
                    "id": hit.id,
                    "vector": getattr(hit, "vector", None),
                    "payload": hit.payload
                }
            return None
        except Exception as e:
            logger.error(f"[QdrantProvider] Get scroll failed in Qdrant collection {collection_name}: {e}")
            raise e
