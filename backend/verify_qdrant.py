import asyncio
from qdrant_client import QdrantClient
from app.vector_store.core import vector_store_config

def main():
    print("--- QDRANT INSPECTION ---")
    client = QdrantClient(url=vector_store_config.QDRANT_URL, api_key=vector_store_config.QDRANT_API_KEY)
    
    collections = client.get_collections().collections
    col_names = [c.name for c in collections]
    
    job_exists = vector_store_config.JOB_COLLECTION in col_names
    cand_exists = vector_store_config.CANDIDATE_COLLECTION in col_names
    
    print(f"JOB_COLLECTION ({vector_store_config.JOB_COLLECTION}) exists: {job_exists}")
    print(f"CANDIDATE_COLLECTION ({vector_store_config.CANDIDATE_COLLECTION}) exists: {cand_exists}")
    
    if job_exists:
        job_info = client.get_collection(vector_store_config.JOB_COLLECTION)
        print(f"\n[JOB_COLLECTION]")
        print(f"Vector Count: {job_info.points_count}")
        print(f"Payload Schema: {list(job_info.payload_schema.keys()) if job_info.payload_schema else []}")
        
        # Get one point to check payload
        res = client.scroll(collection_name=vector_store_config.JOB_COLLECTION, limit=1)
        if res[0]:
            print(f"Sample Payload Keys: {list(res[0][0].payload.keys())}")
        else:
            print("No points found in JOB_COLLECTION")

    if cand_exists:
        cand_info = client.get_collection(vector_store_config.CANDIDATE_COLLECTION)
        print(f"\n[CANDIDATE_COLLECTION]")
        print(f"Vector Count: {cand_info.points_count}")
        print(f"Payload Schema: {list(cand_info.payload_schema.keys()) if cand_info.payload_schema else []}")

if __name__ == "__main__":
    main()
