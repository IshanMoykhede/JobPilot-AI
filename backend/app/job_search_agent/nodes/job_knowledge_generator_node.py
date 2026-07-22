import hashlib
from app.job_search_agent.state import JobSearchState
from app.job_search_agent.services.llm_service import generate_job_knowledge
from app.job_search_agent.utils.token_batcher import create_token_batches
from app.job_search_agent.prompts.job_knowledge_prompt import JOB_KNOWLEDGE_SYSTEM_PROMPT
from app.core.database import SessionLocal
from app.job_search_agent.models.job_knowledge import JobKnowledge, JobKnowledgeStatus
from app.job_search_agent.utils.logger import agent_logger

def generate_job_hash(title: str, company: str) -> str:
    """Generates a stable hash for a job based on title and company."""
    raw_str = f"{title}_{company}".lower().encode('utf-8')
    return hashlib.md5(raw_str).hexdigest()

def job_knowledge_generator_node(state: JobSearchState):
    """
    Checks the database for existing JobKnowledge via hash.
    If not found, processes raw jobs in batches using the LLM to generate JobKnowledge.
    """
    agent_logger.info("=== [NODE 3] START: job_knowledge_generator_node ===")
    
    raw_jobs = state.get("raw_jobs", [])
    if not raw_jobs:
        agent_logger.warning("No raw_jobs found in state, skipping.")
        agent_logger.info("=== [NODE 3] END: job_knowledge_generator_node ===")
        return {"structured_jobs": []}

    db = SessionLocal()
    structured_jobs = []
    jobs_to_process = []
    
    try:
        # Step 1: Deduplication Check
        for raw_job in raw_jobs:
            title = raw_job.get("title", "")
            company = raw_job.get("company_name", "")
            job_hash = generate_job_hash(title, company)
            
            # Check DB
            existing_knowledge = db.query(JobKnowledge).filter(JobKnowledge.job_hash == job_hash).first()
            
            if existing_knowledge and existing_knowledge.processing_status == JobKnowledgeStatus.EXTRACTED:
                # We already processed this job
                # Convert the SQLAlchemy model back to Pydantic schema
                from app.job_search_agent.schemas.job_knowledge import JobKnowledge as JobKnowledgeSchema
                
                if existing_knowledge.raw_knowledge:
                    schema_obj = JobKnowledgeSchema(**existing_knowledge.raw_knowledge)
                else:
                    # Legacy fallback
                    schema_obj = JobKnowledgeSchema(
                        job_title=existing_knowledge.title,
                        company_name=existing_knowledge.company,
                        location=existing_knowledge.location,
                        work_mode="Unknown",
                        employment_type="Unknown", 
                        employment_level="Unknown",
                        minimum_experience_years=None,
                        preferred_experience_years=None,
                        required_degrees=[],
                        preferred_degrees=[],
                        required_specializations=[],
                        preferred_specializations=[],
                        primary_domain="UNKNOWN",
                        secondary_domains=[],
                        required_technologies=existing_knowledge.required_technologies or [],
                        preferred_technologies=existing_knowledge.preferred_technologies or [],
                        required_capabilities=existing_knowledge.capabilities or [],
                        preferred_capabilities=[],
                        required_certifications=[],
                        preferred_certifications=[],
                        responsibilities=[],
                        benefits=[],
                        salary_information=None,
                        industry=None
                    )
                structured_jobs.append({"id": str(existing_knowledge.id), "job_knowledge": schema_obj})
            else:
                # Needs LLM processing
                # Save the hash into the dict so we can use it later
                raw_job["_internal_hash"] = job_hash
                jobs_to_process.append(raw_job)
                
        print(f"Found {len(structured_jobs)} jobs already extracted in DB. {len(jobs_to_process)} jobs need LLM processing.")
        agent_logger.info(f"Deduplication complete: {len(structured_jobs)} jobs cached, {len(jobs_to_process)} jobs need LLM processing.")

        # Step 2: Process unknown jobs with LLM
        if jobs_to_process:
            batches = create_token_batches(
                jobs=jobs_to_process,
                system_prompt=JOB_KNOWLEDGE_SYSTEM_PROMPT,
                max_context_tokens=10000, # Strict 10k limit
            )

            for idx, batch in enumerate(batches):
                print(f"Processing LLM Batch {idx + 1}/{len(batches)} ({len(batch)} jobs)...")
                agent_logger.debug(f"Sending Batch {idx + 1}/{len(batches)} to LLM with {len(batch)} jobs...")
                
                response = generate_job_knowledge(batch)
                
                agent_logger.debug(f"Batch {idx + 1} processed successfully. Received {len(response.jobs)} structured jobs.")
                
                # Also save them to DB for future use and append to structured jobs
                for idx_job, structured_job in enumerate(response.jobs):
                    if idx_job < len(batch):
                        job_hash = batch[idx_job]["_internal_hash"]
                        
                        raw_knowledge_dict = structured_job.model_dump()
                        # Inject raw SerpAPI data that wasn't part of the LLM schema
                        raw_knowledge_dict["original_description"] = batch[idx_job].get("description")
                        raw_knowledge_dict["original_extensions"] = batch[idx_job].get("detected_extensions")
                        
                        # Create new DB record
                        new_db_record = JobKnowledge(
                            job_hash=job_hash,
                            title=structured_job.job_title,
                            company=structured_job.company_name,
                            location=structured_job.location,
                            apply_url=batch[idx_job].get("apply_link"),
                            required_technologies=structured_job.required_technologies,
                            preferred_technologies=structured_job.preferred_technologies,
                            capabilities=structured_job.required_capabilities,
                            raw_knowledge=raw_knowledge_dict,
                            processing_status=JobKnowledgeStatus.EXTRACTED
                        )
                        db.add(new_db_record)
                        db.flush() # Get the UUID without committing the whole batch yet
                        
                        structured_jobs.append({"id": str(new_db_record.id), "job_knowledge": structured_job})
                
                # Commit after every batch
                db.commit()

    except Exception as e:
        print(f"Error in knowledge generation node: {e}")
        agent_logger.error(f"Error in knowledge generation node: {e}", exc_info=True)
        db.rollback()
        raise e
    finally:
        db.close()
        
    if not structured_jobs:
        agent_logger.error("No jobs could be processed or found in cache.")
        raise RuntimeError("Failed to generate or retrieve knowledge for any jobs in the batch.")

    agent_logger.info(f"=== [NODE 3] END: job_knowledge_generator_node (Total Output: {len(structured_jobs)} jobs) ===")
    return {
        "structured_jobs": structured_jobs
    }
