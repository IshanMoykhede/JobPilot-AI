from app.core.config import settings

# Default configuration for embedding models and parameters
EMBEDDING_PROVIDER = settings.EMBEDDING_PROVIDER if hasattr(settings, "EMBEDDING_PROVIDER") else "fastembed"
EMBEDDING_MODEL = settings.EMBEDDING_MODEL if hasattr(settings, "EMBEDDING_MODEL") else "BAAI/bge-small-en-v1.5"
EMBEDDING_DIMENSION = settings.EMBEDDING_DIMENSION if hasattr(settings, "EMBEDDING_DIMENSION") else 384
EMBEDDING_SCHEMA_VERSION = "v1"
EMBEDDING_BATCH_SIZE = settings.EMBEDDING_BATCH_SIZE if hasattr(settings, "EMBEDDING_BATCH_SIZE") else 20
