import asyncio
from app.vector_store.providers.qdrant_provider import QdrantProvider
from app.vector_store.core import vector_store_config

def main():
    print("--- TRIGGERING INITIALIZATION ---")
    provider = QdrantProvider(url=vector_store_config.QDRANT_URL, api_key=vector_store_config.QDRANT_API_KEY)
    
    print("\n--- VERIFYING SCHEMA ---")
    client = provider.client
    job_info = client.get_collection(vector_store_config.JOB_COLLECTION)
    
    print(f"Collection: {vector_store_config.JOB_COLLECTION}")
    print(f"Payload Indexes: {list(job_info.payload_schema.keys()) if job_info.payload_schema else []}")

if __name__ == "__main__":
    main()
