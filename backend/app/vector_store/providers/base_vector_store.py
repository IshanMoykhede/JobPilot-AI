from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseVectorStore(ABC):
    @abstractmethod
    def exists(self, collection_name: str, doc_hash: str) -> bool:
        """
        Checks if a document with the given semantic_document_hash exists.
        """
        pass

    @abstractmethod
    def upsert(self, collection_name: str, point_id: str, vector: List[float], payload: Dict[str, Any]) -> None:
        """
        Upserts a single point with its vector and payload metadata.
        """
        pass

    @abstractmethod
    def upsert_batch(self, collection_name: str, points: List[Dict[str, Any]]) -> None:
        """
        Upserts a batch of points. Each point contains keys: "id", "vector", "payload".
        """
        pass

    @abstractmethod
    def search(self, collection_name: str, query_vector: List[float], limit: int = 100, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Performs vector similarity search and returns matches with scores and payloads.
        """
        pass

    @abstractmethod
    def get(self, collection_name: str, filter_field: str, filter_value: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single record from the collection matching a filter.
        """
        pass
