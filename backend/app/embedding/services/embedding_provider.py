import hashlib
import random
import logging
from abc import ABC, abstractmethod
from typing import List
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

logger = logging.getLogger(__name__)

class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        pass

class FastEmbedEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self.client = FastEmbedEmbeddings(model_name=self.model_name)

    def generate_embedding(self, text: str) -> List[float]:
        logger.info(f"[FastEmbedEmbeddingProvider] Embedding single document (model={self.model_name})")
        return self.client.embed_query(text)

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        logger.info(f"[FastEmbedEmbeddingProvider] Embedding batch of {len(texts)} documents (model={self.model_name})")
        return self.client.embed_documents(texts)

class MockEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def generate_embedding(self, text: str) -> List[float]:
        logger.info(f"[MockEmbeddingProvider] Seeding mock vector of dim={self.dimension}")
        hasher = hashlib.sha256(text.encode("utf-8"))
        seed = int(hasher.hexdigest()[:8], 16)
        rng = random.Random(seed)
        return [rng.uniform(-1.0, 1.0) for _ in range(self.dimension)]

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        logger.info(f"[MockEmbeddingProvider] Batch seeding {len(texts)} mock vectors")
        return [self.generate_embedding(text) for text in texts]
