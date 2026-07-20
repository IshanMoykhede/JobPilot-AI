from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams

from app.job_search_agent.schemas.job_knowledge import JobKnowledge
from app.core.config import settings

# --------------------------------------------------------
# Qdrant Client Initialization
# --------------------------------------------------------

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY
)

# --------------------------------------------------------
# Service
# --------------------------------------------------------

def store_jobs(
    structured_jobs: list[JobKnowledge],
    embeddings: list[list[float]]
) -> None:
    """
    Stores structured jobs and their embeddings into Qdrant.
    """
    collection_name = "job_embeddings_testing"
    
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=384, # bge-small-en-v1.5 has 384 dimensions
                distance=Distance.COSINE 
            )
        )

    points = []

    for index, (job, embedding) in enumerate(
        zip(structured_jobs, embeddings)
    ):
        # We use a hash or UUID for the ID in production, but we can fall back to a random UUID if needed.
        # For now we'll hash the job title and company name to get a consistent integer, 
        # or just let Qdrant assign a UUID. Wait, Qdrant allows string UUIDs!
        
        # We need a stable ID to avoid duplicates.
        import hashlib
        stable_id_str = f"{job.job_title}_{job.company_name}".lower().encode('utf-8')
        stable_id = hashlib.md5(stable_id_str).hexdigest()
        
        # Convert MD5 to valid UUID format for Qdrant (8-4-4-4-12)
        import uuid
        stable_uuid = str(uuid.UUID(stable_id))

        point = PointStruct(
            id=stable_uuid,
            vector=embedding,
            payload=job.model_dump()
        )
        points.append(point)

    if points:
        client.upsert(
            collection_name=collection_name,
            points=points
        )
        print(f"Successfully stored {len(points)} jobs in Qdrant.")


def store_candidate(candidate_id: str, embedding: list[float]) -> None:
    """
    Stores a candidate's embedding in Qdrant.
    """
    collection_name = "candidate_knowledge"
    
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE 
            )
        )

    point = PointStruct(
        id=candidate_id,
        vector=embedding,
        payload={}
    )

    client.upsert(
        collection_name=collection_name,
        points=[point]
    )
    print(f"Successfully stored candidate {candidate_id} in Qdrant.")


def retrieve_candidate_embedding(candidate_id: str) -> list[float]:
    """
    Retrieves the candidate embedding from Qdrant.
    """
    result = client.retrieve(
        collection_name="candidate_knowledge", # Production collection for candidates
        ids=[candidate_id],
        with_vectors=True,
        with_payload=False
    )

    if not result:
        raise ValueError(
            f"No candidate found with ID {candidate_id}"
        )

    return result[0].vector


def search_similar_jobs(
    candidate_embedding: list[float],
    limit: int = 10
) -> list[JobKnowledge]:
    """
    Searches the job embedding collection using the
    candidate embedding and returns the top matching jobs.
    """
    results = client.query_points(
        collection_name="job_embeddings_testing",
        query=candidate_embedding,
        limit=limit,
        with_payload=True,
        with_vectors=False
    )

    matched_jobs = []

    for point in results.points:
        if point.payload:
            print(f"Match Score: {point.score:.4f} | Job: {point.payload.get('job_title')}")
            job = JobKnowledge(**point.payload)
            matched_jobs.append(job)

    return matched_jobs
