import asyncio
from qdrant_client import QdrantClient
from app.vector_store.core import vector_store_config

def main():
    print("--- DELETING JOB_COLLECTION ---")
    client = QdrantClient(url=vector_store_config.QDRANT_URL, api_key=vector_store_config.QDRANT_API_KEY)
    
    if client.collection_exists(vector_store_config.JOB_COLLECTION):
        client.delete_collection(vector_store_config.JOB_COLLECTION)
        print(f"Collection {vector_store_config.JOB_COLLECTION} deleted successfully.")
    else:
        print(f"Collection {vector_store_config.JOB_COLLECTION} does not exist.")

if __name__ == "__main__":
    main()
