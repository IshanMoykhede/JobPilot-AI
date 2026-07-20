from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.job_search import JobSearchRequest, JobSearchResponse, ResumeJobSearchResponse
from app.job_search_agent.models.job_searches import JobSearch, SearchStatus
from app.job_search_agent.graph import get_job_search_app
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.services.profile_service import get_candidate_profile_by_user_id

router = APIRouter(prefix="/api/job-search", tags=["Job Search Agent"])

from fastapi.responses import StreamingResponse
import json

@router.post("/run")
def run_job_search(request: JobSearchRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Initiates a new job search session.
    Creates a database record and triggers the LangGraph agent in a streaming manner via SSE.
    """
    try:
        from app.job_search_agent.utils.logger import agent_logger
        
        # Look up profile
        profile = get_candidate_profile_by_user_id(db, current_user.id)
        if not profile:
            raise HTTPException(status_code=404, detail="Candidate profile not found. Please complete onboarding.")
            
        candidate_profile_id = str(profile.id)

        agent_logger.info(f"\\\n"
                          f"==========================================================\n"
                          f"=== [NEW JOB SEARCH] Candidate: {candidate_profile_id}\n"
                          f"=== [NEW JOB SEARCH] Query: {request.query}\n"
                          f"==========================================================")
        
        # 1. Create a new search record to get our UUID (Thread ID)
        new_search = JobSearch(
            candidate_profile_id=candidate_profile_id,
            original_query=request.query,
            status=SearchStatus.PROCESSING
        )
        db.add(new_search)
        db.commit()
        db.refresh(new_search)
        
        thread_id = str(new_search.id)

        # 2. Get the compiled graph
        agent = get_job_search_app()

        # 3. Define Initial State
        initial_state = {
            "job_search_id": thread_id,
            "candidate_profile_id": candidate_profile_id,
            "user_query": request.query
        }
        config = {"configurable": {"thread_id": thread_id}}

        # 4. Generator function for Server-Sent Events (SSE)
        def event_stream():
            try:
                # Use .stream() with mode="updates" to yield as each node finishes
                for event in agent.stream(initial_state, config=config, stream_mode="updates"):
                    # event is a dict containing { node_name: node_output }
                    for node_name, node_output in event.items():
                        data = json.dumps({"node": node_name, "status": "completed"})
                        yield f"data: {data}\n\n"
                
                # 5. Mark as completed
                new_search.status = SearchStatus.COMPLETED
                db.commit()
                agent_logger.info(f"=== [END JOB SEARCH] Successfully processed in thread: {thread_id} ===")
                
                # Yield final DONE event
                yield f"data: {json.dumps({'node': 'DONE', 'thread_id': thread_id})}\n\n"
                
            except Exception as e:
                # Mark as failed in DB
                new_search.status = SearchStatus.FAILED
                db.commit()
                agent_logger.error(f"=== [CRASH] Pipeline failed for query '{request.query}': {e}", exc_info=True)
                yield f"data: {json.dumps({'node': 'ERROR', 'detail': str(e), 'thread_id': thread_id})}\n\n"

        # Return StreamingResponse with text/event-stream content type
        return StreamingResponse(event_stream(), media_type="text/event-stream")

    except Exception as e:
        from app.job_search_agent.utils.logger import agent_logger
        agent_logger.error(f"=== [CRASH] Initial setup failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during the job search setup: {str(e)}"
        )


@router.post("/resume/{thread_id}", status_code=status.HTTP_200_OK)
def resume_job_search(thread_id: str, db: Session = Depends(get_db)):
    """
    Resumes a failed or paused job search session using the Checkpointer and streams the result.
    """
    from app.job_search_agent.utils.logger import agent_logger

    try:
        # 1. Verify it exists
        job_search = db.query(JobSearch).filter(JobSearch.id == thread_id).first()
        if not job_search:
            raise HTTPException(status_code=404, detail="Job search session not found.")

        # Update status to processing again
        job_search.status = SearchStatus.PROCESSING
        db.commit()

        # 2. Get compiled graph
        agent = get_job_search_app()
        config = {"configurable": {"thread_id": thread_id}}

        def event_stream():
            try:
                # 3. Check if there is an existing checkpoint
                snapshot = agent.get_state(config)
                
                if not snapshot.values:
                    # If it crashed before saving ANY checkpoint, we must restart it with full input
                    input_state = {
                        "job_search_id": thread_id,
                        "candidate_profile_id": str(job_search.candidate_profile_id),
                        "user_query": job_search.original_query
                    }
                else:
                    # Resume execution from checkpoint by passing None as state
                    input_state = None

                for event in agent.stream(input_state, config=config, stream_mode="updates"):
                    for node_name, node_output in event.items():
                        data = json.dumps({"node": node_name, "status": "completed"})
                        yield f"data: {data}\n\n"
                
                # Mark as completed
                job_search.status = SearchStatus.COMPLETED
                db.commit()
                agent_logger.info(f"=== [RESUME COMPLETE] Successfully processed in thread: {thread_id} ===")
                
                yield f"data: {json.dumps({'node': 'DONE', 'thread_id': thread_id})}\n\n"
                
            except Exception as e:
                # Mark as failed
                job_search.status = SearchStatus.FAILED
                db.commit()
                agent_logger.error(f"=== [CRASH] Pipeline failed on resume for thread '{thread_id}': {e}", exc_info=True)
                yield f"data: {json.dumps({'node': 'ERROR', 'detail': str(e), 'thread_id': thread_id})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")
        
    except HTTPException:
        raise
    except Exception as e:
        agent_logger.error(f"=== [CRASH] Initial setup failed on resume: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during resume setup: {str(e)}"
        )

@router.get("/history", status_code=status.HTTP_200_OK)
def get_search_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Fetches the history of job searches for a specific candidate profile.
    """
    try:
        profile = get_candidate_profile_by_user_id(db, current_user.id)
        if not profile:
            return []

        history = db.query(JobSearch).filter(JobSearch.candidate_profile_id == str(profile.id)).order_by(JobSearch.created_at.desc()).all()
        return [
            {
                "id": str(h.id),
                "original_query": h.original_query,
                "optimized_role": h.optimized_role,
                "optimized_location": h.optimized_location,
                "status": h.status.value,
                "created_at": h.created_at
            }
            for h in history
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching history: {str(e)}"
        )

@router.get("/{thread_id}/results", status_code=status.HTTP_200_OK)
def get_search_results(thread_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Fetches the scored job results for a completed job search session.
    """
    from app.job_search_agent.models.job_match_scores import JobMatchScore
    from sqlalchemy.orm import joinedload

    try:
        # Verify search exists
        job_search = db.query(JobSearch).filter(JobSearch.id == thread_id).first()
        if not job_search:
            raise HTTPException(status_code=404, detail="Job search session not found.")

        # Fetch scores and eager load job knowledge
        scores = db.query(JobMatchScore).options(joinedload(JobMatchScore.job_knowledge)).filter(
            JobMatchScore.job_search_id == thread_id
        ).order_by(JobMatchScore.final_score.desc()).all()

        results = []
        for rank, score in enumerate(scores, start=1):
            knowledge = score.job_knowledge
            results.append({
                "job_match_score_id": str(score.id),
                "title": knowledge.title,
                "company": knowledge.company,
                "location": knowledge.location,
                "apply_url": knowledge.apply_url,
                "work_mode": knowledge.raw_knowledge.get("work_mode") if knowledge.raw_knowledge else "Unknown",
                "employment_type": knowledge.raw_knowledge.get("employment_type") if knowledge.raw_knowledge else None,
                "salary_information": knowledge.raw_knowledge.get("salary_information") if knowledge.raw_knowledge else None,
                "original_description": knowledge.raw_knowledge.get("original_description") if knowledge.raw_knowledge else None,
                "original_extensions": knowledge.raw_knowledge.get("original_extensions") if knowledge.raw_knowledge else [],
                "final_score": score.final_score,
                "rank": rank,
                "matching_skills": score.matching_skills or [],
                "missing_skills": score.missing_skills or [],
                "insight_text": score.ai_explanation.get("reasoning") if score.ai_explanation else None
            })

        return {
            "thread_id": thread_id,
            "query": job_search.original_query,
            "status": job_search.status.value,
            "jobs": results
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching results: {str(e)}"
        )


from pydantic import BaseModel

class RenameSearchRequest(BaseModel):
    name: str

@router.put("/{thread_id}")
def rename_job_search(
    thread_id: str, 
    request: RenameSearchRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Renames a past job search session."""
    profile = get_candidate_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
        
    job_search = db.query(JobSearch).filter(
        JobSearch.id == thread_id,
        JobSearch.candidate_profile_id == profile.id
    ).first()
    
    if not job_search:
        raise HTTPException(status_code=404, detail="Job search not found")
        
    job_search.original_query = request.name
    db.commit()
    return {"message": "Job search renamed successfully"}

@router.delete("/{thread_id}")
def delete_job_search(
    thread_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Deletes a job search session and cascades to delete all scores."""
    profile = get_candidate_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
        
    job_search = db.query(JobSearch).filter(
        JobSearch.id == thread_id,
        JobSearch.candidate_profile_id == profile.id
    ).first()
    
    if not job_search:
        raise HTTPException(status_code=404, detail="Job search not found")
        
    db.delete(job_search)
    db.commit()
    return {"message": "Job search deleted successfully"}
