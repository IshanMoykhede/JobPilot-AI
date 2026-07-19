import os
from app.core.config import settings

# Generic settings loaded from application configurations
QDRANT_URL = settings.QDRANT_URL
QDRANT_API_KEY = settings.QDRANT_API_KEY

# Collection configuration
DIMENSION = 384 # bge-small-en-v1.5 dimension

# Subsystem specific internal variables (decoupled from root config)
VECTOR_STORE_PROVIDER = "qdrant"
CANDIDATE_COLLECTION = "candidate_vectors"
JOB_COLLECTION = "job_vectors"
DEFAULT_DISTANCE = "Cosine"
UPSERT_BATCH_SIZE = 20
