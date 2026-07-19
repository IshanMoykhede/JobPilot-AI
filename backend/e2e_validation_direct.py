import asyncio
import uuid
from app.core.database import SessionLocal

# Pre-load all SQLAlchemy models for mapper resolution
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_insights import CandidateInsights
from app.conversation.models.conversation import Conversation
from app.job_search.models.search_workspace import SearchWorkspace
from app.job_search.models.job_search_result import JobSearchResult
from app.job_search.models.job_knowledge import JobKnowledge
from app.job_search.services.retrieval_pipeline_service import RetrievalPipelineService
from app.vector_store.providers.qdrant_provider import QdrantProvider


async def main():
    db = SessionLocal()
    # Get a real candidate profile ID
    from app.job_search.models.search_workspace import SearchWorkspace
    w_old = db.query(SearchWorkspace).first()
    if not w_old:
        print("No old workspaces found in DB to steal a candidate ID from!")
        return
    candidate_id = w_old.candidate_profile_id
    
    query = "Backend Developer Internship Pune"
    print(f"Executing pipeline for query: {query}")
    
    try:
        result = await RetrievalPipelineService.execute_pipeline(
            db=db,
            candidate_profile_id=candidate_id,
            original_query=query,
            location=None
        )
        workspace_id = result['workspace_id']
        print(f"Pipeline executed. Workspace ID: {workspace_id}")
    except Exception as e:
        print(f"Pipeline failed: {e}")
        return

    w = db.query(SearchWorkspace).filter_by(id=workspace_id).first()
    
    print("\n--- Validation Report ---")
    print(f"1. Query received from frontend: {w.original_query}")
    print(f"2. Exact payload sent to SerpAPI (optimized_query): {w.optimized_query}")
    
    results = db.query(JobSearchResult).filter_by(workspace_id=w.id).all()
    print(f"3. Number of jobs returned (raw fetched): {w.total_jobs_fetched}")
    print(f"4. Number of JobSearchResults created: {len(results)}")
    
    knowledge_records = db.query(JobKnowledge).filter(JobKnowledge.id.in_([r.job_knowledge_id for r in results if r.job_knowledge_id])).all()
    print(f"5. Number of JobKnowledge records generated: {len(knowledge_records)}")
    
    try:
        from app.vector_store.core import vector_store_config
        qdrant = QdrantProvider(url=vector_store_config.QDRANT_URL, api_key=vector_store_config.QDRANT_API_KEY)
        count_response = qdrant.client.count(collection_name="job_vectors")
        vector_count = count_response.count
    except Exception as e:
        vector_count = f"Error: {e}"
    print(f"6. Number of Qdrant vectors total in collection: {vector_count}")
    
    metadata = w.search_metadata or {}
    print(f"7. Provider used: {metadata.get('provider')}")
    print(f"8. Jobs received by provider: {metadata.get('jobs_received')}")
    print(f"9. Provider status: {metadata.get('provider_status')}")

if __name__ == "__main__":
    asyncio.run(main())
