from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams, Filter, FieldCondition, MatchValue

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
    structured_jobs: list[dict],
    embeddings: list[list[float]],
    conversation_id: str = None
) -> None:
    """
    Stores structured jobs and their embeddings into Qdrant.
    Uses the Postgres UUID as the Qdrant Point ID.
    Injects job_id and conversation_id into the payload.
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
        
    try:
        # Idempotent operation to ensure the index exists for filtering
        client.create_payload_index(
            collection_name=collection_name,
            field_name="conversation_id",
            field_schema="keyword"
        )
    except Exception as e:
        pass # Index likely already exists or client handles idempotency internally

    points = []

    for index, (job_dict, embedding) in enumerate(
        zip(structured_jobs, embeddings)
    ):
        postgres_id = job_dict["id"]
        job_knowledge = job_dict["job_knowledge"]
        
        payload = job_knowledge.model_dump()
        payload["job_id"] = postgres_id
        if conversation_id:
            payload["conversation_id"] = conversation_id
            
        point = PointStruct(
            id=postgres_id,
            vector=embedding,
            payload=payload
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
    conversation_id: str = None,
    limit: int = 10
) -> list[dict]:
    """
    Searches the job embedding collection using the
    candidate embedding and returns the top matching jobs.
    Optionally filters by conversation_id to only search within the current session.
    """
    query_filter = None
    if conversation_id:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="conversation_id",
                    match=MatchValue(value=conversation_id)
                )
            ]
        )
        
    results = client.query_points(
        collection_name="job_embeddings_testing",
        query=candidate_embedding,
        query_filter=query_filter,
        limit=limit,
        with_payload=True,
        with_vectors=False
    )

    matched_jobs = []

    for point in results.points:
        if point.payload:
            print(f"Match Score: {point.score:.4f} | Job: {point.payload.get('job_title')}")
            # Ensure we don't pass the internal Qdrant-injected keys (like job_id) into JobKnowledge if it breaks validation
            # JobKnowledge accepts the raw payload thanks to Extra.ignore or by simply dumping the fields it knows.
            # Actually, `JobKnowledge(**point.payload)` works perfectly.
            job = JobKnowledge(**point.payload)
            matched_jobs.append({
                "id": point.payload.get("job_id"),
                "job_knowledge": job
            })

    return matched_jobs
