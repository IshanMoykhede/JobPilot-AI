from enum import Enum

class EmbeddingProviderType(str, Enum):
    GEMINI = "gemini"
    MOCK = "mock"
