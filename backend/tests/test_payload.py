import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.job_search.models.search_workspace import SearchWorkspace
from app.job_search_agent.presentation.job_search_presentation_builder import JobSearchPresentationBuilder
from app.job_search_agent.explanation.schemas.explanation import JobExplanation
import json

def test():
    db = SessionLocal()
    workspace = db.query(SearchWorkspace).order_by(SearchWorkspace.created_at.desc()).first()
    
    # We will simulate the fallbacks being passed to the builder
    # First, get the jobs that should have been ranked
    from app.job_search.models.job_search_result import JobSearchResult
    jobs = db.query(JobSearchResult).filter(
        JobSearchResult.workspace_id == workspace.id,
        JobSearchResult.final_score.isnot(None)
    ).order_by(JobSearchResult.final_score.desc()).all()
    
    fallbacks = []
    for j in jobs[:5]:
        fallbacks.append(JobExplanation(
            job_id=str(j.id),
            summary="Fallback summary",
            recommendation="Fallback rec",
            confidence="Medium",
            reasoning="Fallback reasoning"
        ))
        
    try:
        response_dto = JobSearchPresentationBuilder.build_response(
            db=db,
            workspace_id=workspace.id,
            explanations=fallbacks
        )
        print("PAYLOAD BUILT SUCCESSFULLY!")
        print(json.dumps(response_dto.model_dump(), indent=2))
    except Exception as e:
        print(f"FAILED TO BUILD PAYLOAD: {e}")

if __name__ == "__main__":
    test()
