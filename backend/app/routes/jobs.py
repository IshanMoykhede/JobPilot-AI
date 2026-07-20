# import logging
# from uuid import UUID
# from typing import Optional
# from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
# from pydantic import BaseModel
# from sqlalchemy.orm import Session
# from app.core.database import get_db
# from app.models.user import User
# from app.dependencies.auth import get_current_user
# from app.services.profile_service import get_candidate_profile_by_user_id
# DEPRECATED FILE: This entire route file used the old `app.job_search` 
# which has been replaced by the LangGraph `app.job_search_agent`.
# Keeping file for reference but removing imports to fix IDE errors.
# 
# from app.job_search.services.retrieval_pipeline_service import RetrievalPipelineService
# from app.job_search.services.job_knowledge_engine import JobKnowledgeEngine
# from app.job_search.schemas.job_search import JobSearchRequest
# 
# logger = logging.getLogger(__name__)
# 
# router = APIRouter(
#     prefix="/jobs",
#     tags=["Job Search"]
# )
# 
# class JobSearchApiRequest(JobSearchRequest):
#     conversation_id: Optional[UUID] = None
# 
# class RetrievalPipelineResponse(BaseModel):
#     conversation_id: UUID
#     workspace_id: UUID
#     number_of_jobs_retrieved: int
# 
# def extract_knowledge_bg(workspace_id: UUID):
#     """
#     Helper function to run the Job Knowledge Engine asynchronously in the background.
#     Opens a dedicated database session to prevent sharing/closed issues.
#     """
#     from app.core.database import SessionLocal
#     import asyncio
#     db = SessionLocal()
#     try:
#         logger.info(f"[JobsEndpoint] Starting background job knowledge extraction for workspace {workspace_id}")
#         asyncio.run(JobKnowledgeEngine.generate_job_knowledge_for_workspace(db, workspace_id))
#         logger.info(f"[JobsEndpoint] Finished background job knowledge extraction for workspace {workspace_id}")
#     except Exception as e:
#         logger.error(f"[JobsEndpoint] Background job knowledge extraction failed: {e}")
#     finally:
#         db.close()
# 
# @router.post("/search", response_model=RetrievalPipelineResponse, status_code=status.HTTP_201_CREATED)
# async def search_jobs_endpoint(
#     req: JobSearchApiRequest,
#     background_tasks: BackgroundTasks,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     Triggers the end-to-end atomic job search retrieval pipeline.
#     Creates or reuses conversations and search workspaces, optimizes queries,
#     fetches from SerpAPI/Mock, parses, and persists results.
#     Triggers structured Job Knowledge extraction asynchronously in the background.
#     """
#     logger.info(f"[JobsEndpoint] Search requested by user={current_user.id} query='{req.query}'")
#     
#     # 1. Fetch candidate profile
#     profile = get_candidate_profile_by_user_id(db, current_user.id)
#     if not profile:
#         logger.error(f"[JobsEndpoint] Profile check failed for user {current_user.id}. No profile found.")
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Candidate profile does not exist. Please complete onboarding first."
#         )
# 
#     # 2. Execute retrieval pipeline
#     try:
#         location_filter = req.filters.locations[0] if (req.filters and req.filters.locations) else None
#         
#         result = await RetrievalPipelineService.execute_pipeline(
#             db=db,
#             candidate_profile_id=profile.id,
#             original_query=req.query,
#             conversation_id=req.conversation_id,
#             location=location_filter
#         )
#         
#         # Trigger structured knowledge extraction asynchronously in the background
#         background_tasks.add_task(extract_knowledge_bg, result["workspace_id"])
#         
#         return RetrievalPipelineResponse(
#             conversation_id=result["conversation_id"],
#             workspace_id=result["workspace_id"],
#             number_of_jobs_retrieved=result["number_of_jobs_retrieved"]
#         )
#     except Exception as e:
#         logger.error(f"[JobsEndpoint] Retrieval pipeline failed: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Job retrieval failed: {str(e)}"
#         )
# 
# from app.presentation.job_search_response_assembler import JobSearchResponseAssembler
# from app.presentation.schemas.job_search import JobCardResponse, JobSearchResponse
# 
# PIPELINE_STAGE_MAP = {
#     "CREATED": {"step": 0, "label": "Initializing workspace...", "icon": "rocket_launch"},
#     "FETCHING": {"step": 1, "label": "Scouring the internet for jobs...", "icon": "travel_explore"},
#     "RAW_JOBS_READY": {"step": 2, "label": "Extracting structured job requirements...", "icon": "psychology"},
#     "KNOWLEDGE_GENERATING": {"step": 2, "label": "Extracting structured job requirements...", "icon": "psychology"},
#     "EMBEDDING": {"step": 3, "label": "Running semantic embeddings...", "icon": "hub"},
#     "MATCHING": {"step": 4, "label": "Calculating match scores...", "icon": "compare_arrows"},
#     "EXPLAINING": {"step": 5, "label": "Drafting candidate guidance...", "icon": "auto_awesome"},
#     "READY": {"step": 6, "label": "Your results are ready!", "icon": "check_circle"},
#     "FAILED": {"step": -1, "label": "Something went wrong.", "icon": "error"},
# }
# 
# @router.get("/workspace/{workspace_id}/status")
# async def get_workspace_status(
#     workspace_id: UUID,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Lightweight polling endpoint for the frontend to track pipeline progress.
#     Returns the current stage name, step index, and a user-friendly label.
#     """
#     from app.job_search.models.search_workspace import SearchWorkspace
#     
#     ws = db.query(SearchWorkspace).filter(SearchWorkspace.id == workspace_id).first()
#     if not ws:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found.")
#     
#     current_status = ws.processing_status.value if ws.processing_status else "CREATED"
#     stage_info = PIPELINE_STAGE_MAP.get(current_status, PIPELINE_STAGE_MAP["CREATED"])
#     
#     return {
#         "workspace_id": str(ws.id),
#         "status": current_status,
#         "step": stage_info["step"],
#         "total_steps": 6,
#         "label": stage_info["label"],
#         "icon": stage_info["icon"],
#         "is_complete": current_status == "READY",
#         "is_failed": current_status == "FAILED",
#         "jobs_fetched": ws.total_jobs_fetched or 0
#     }
# 
# @router.get("/workspace/{workspace_id}/results", response_model=JobSearchResponse)
# async def get_workspace_results(
#     workspace_id: UUID,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Returns the fully assembled JobSearchResponse for a completed workspace.
#     """
#     return JobSearchResponseAssembler.build_response(db, workspace_id)
# 
# @router.get("/{job_result_id}/details", response_model=JobCardResponse)
# async def get_job_details_endpoint(
#     job_result_id: UUID,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Returns the fully assembled, presentation-ready JobCardResponse DTO.
#     This hides all internal AI reasoning schemas from the frontend.
#     """
#     from app.job_search.models.job_search_result import JobSearchResult
#     
#     db_res = db.query(JobSearchResult).filter(JobSearchResult.id == job_result_id).first()
#     if not db_res:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Job search result not found."
#         )
#         
#     return JobSearchResponseAssembler.build_job_card(db_res)
# 
