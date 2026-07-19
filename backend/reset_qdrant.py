from app.vector_store.providers.qdrant_provider import QdrantProvider
from app.vector_store.core.vector_store_config import QDRANT_URL, QDRANT_API_KEY, CANDIDATE_COLLECTION, JOB_COLLECTION

print(f"Reinitializing Qdrant Collections at {QDRANT_URL}...")
provider = QdrantProvider(url=QDRANT_URL, api_key=QDRANT_API_KEY)
try:
    provider.client.delete_collection(CANDIDATE_COLLECTION)
    provider.client.delete_collection(JOB_COLLECTION)
    print("Deleted old collections.")
except Exception as e:
    print("Error deleting:", e)

# Recreate them
provider._ensure_collection(CANDIDATE_COLLECTION)
provider._ensure_collection(JOB_COLLECTION)
print("Qdrant initialized successfully with new dimensions!")
