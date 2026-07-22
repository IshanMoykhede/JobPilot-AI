from app.job_search_agent.state import JobSearchState
from app.job_search_agent.utils.semantic_formatter import format_job_semantic_document
from app.job_search_agent.services.embedding_service import generate_embeddings
from app.job_search_agent.services.qdrant_service import store_jobs, store_candidate
from app.core.database import SessionLocal
from app.models.candidate_profile import CandidateProfile
from app.job_search_agent.utils.logger import agent_logger
import json

def embedding_store_node(state: JobSearchState):
    """
    Generates embeddings for structured jobs AND the candidate profile, 
    then stores them in Qdrant.
    """
    agent_logger.info("=== [NODE 4] START: embedding_store_node ===")
    
    candidate_profile_id = state.get("candidate_profile_id")
    
    # 1. Embed and store candidate
    if candidate_profile_id:
        db = SessionLocal()
        try:
            from app.models.candidate_insights import CandidateInsights, ArtifactType, InsightStatus
            from app.embedding.services.candidate_document_builder import CandidateDocumentBuilder
            
            insight = db.query(CandidateInsights).filter(
                CandidateInsights.candidate_profile_id == candidate_profile_id,
                CandidateInsights.artifact_type == ArtifactType.CANDIDATE_KNOWLEDGE,
                CandidateInsights.status == InsightStatus.COMPLETED
            ).first()
            
            if insight and insight.artifact_json:
                print(f"Generating embedding for Candidate {candidate_profile_id}...")
                semantic_profile_doc = CandidateDocumentBuilder.build_document(insight.artifact_json)
                
                # Generate embedding (it expects a list of docs)
                candidate_emb = generate_embeddings([semantic_profile_doc])[0]
                
                # Store in Qdrant
                store_candidate(str(candidate_profile_id), candidate_emb)
                agent_logger.debug(f"Successfully generated and stored Candidate {candidate_profile_id} embedding.")
            else:
                agent_logger.warning(f"No completed CandidateInsights found for Candidate {candidate_profile_id}.")
        except Exception as e:
            print(f"Error embedding candidate profile: {e}")
            agent_logger.error(f"Error embedding candidate profile: {e}")
            raise e
        finally:
            db.close()
            
    # 2. Embed and store jobs
    structured_jobs = state.get("structured_jobs", [])
    if structured_jobs:
        print(f"Generating embeddings for {len(structured_jobs)} jobs...")
        agent_logger.debug(f"Generating embeddings for {len(structured_jobs)} jobs...")
        
        # Extract the JobKnowledge objects from the dicts for formatting
        job_knowledge_list = [item["job_knowledge"] for item in structured_jobs]
        
        # Convert into Semantic Documents
        semantic_documents = format_job_semantic_document(job_knowledge_list)
        
        # Generate Embeddings
        embeddings = generate_embeddings(semantic_documents)
        
        # Store in Qdrant passing the full dicts so we keep the DB IDs, plus the conversation ID
        store_jobs(
            structured_jobs=structured_jobs,
            embeddings=embeddings,
            conversation_id=state.get("job_search_id")
        )
        agent_logger.debug(f"Successfully stored {len(embeddings)} job embeddings in Qdrant.")

    agent_logger.info("=== [NODE 4] END: embedding_store_node ===")
    return {}
