import logging
from typing import List, Dict, Any, Optional

from app.vector_store.core import vector_store_config
from app.vector_store.providers.base_vector_store import BaseVectorStore
from app.vector_store.providers.qdrant_provider import QdrantProvider
from app.vector_store.providers.mock_provider import MockVectorStore

logger = logging.getLogger(__name__)

_qdrant_client: Optional[BaseVectorStore] = None
_mock_client: Optional[BaseVectorStore] = None

class VectorStoreService:
    @staticmethod
    def _get_provider() -> BaseVectorStore:
        global _qdrant_client, _mock_client
        
        provider_name = getattr(vector_store_config, "VECTOR_STORE_PROVIDER", "qdrant").lower()
        if provider_name == "qdrant":
            if _qdrant_client is None:
                logger.info("[VectorStoreService] Initializing Qdrant client connection...")
                _qdrant_client = QdrantProvider(
                    url=vector_store_config.QDRANT_URL,
                    api_key=vector_store_config.QDRANT_API_KEY
                )
            return _qdrant_client
        else:
            if _mock_client is None:
                logger.info("[VectorStoreService] Using Mock Vector Store Provider.")
                _mock_client = MockVectorStore()
            return _mock_client

    @staticmethod
    def exists(collection_name: str, doc_hash: str) -> bool:
        provider = VectorStoreService._get_provider()
        return provider.exists(collection_name, doc_hash)

    @staticmethod
    def upsert(collection_name: str, point_id: str, vector: List[float], payload: Dict[str, Any]) -> None:
        provider = VectorStoreService._get_provider()
        provider.upsert(collection_name, point_id, vector, payload)

    @staticmethod
    def upsert_batch(collection_name: str, points: List[Dict[str, Any]]) -> None:
        provider = VectorStoreService._get_provider()
        provider.upsert_batch(collection_name, points)

    @staticmethod
    def search(collection_name: str, query_vector: List[float], limit: int = 100, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        provider = VectorStoreService._get_provider()
        return provider.search(collection_name, query_vector, limit, filter_dict)

    @staticmethod
    def get(collection_name: str, filter_field: str, filter_value: str) -> Optional[Dict[str, Any]]:
        provider = VectorStoreService._get_provider()
        return provider.get(collection_name, filter_field, filter_value)
