from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Pre-load all SQLAlchemy models for mapper resolution
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_insights import CandidateInsights
# from app.conversation.models.conversation import Conversation
# from app.job_search.models.search_workspace import SearchWorkspace
# from app.job_search.models.job_search_result import JobSearchResult
# from app.job_search.models.job_knowledge import JobKnowledge
from app.routes.auth import router as auth_router
from app.routes.candidate_profile import router as profile_router
from app.routes.job_search_routes import router as job_search_router
from app.routes.resume_agent_routes import router as resume_agent_router
from app.routes.resume_agent_v2_routes import router as resume_agent_v2_router
# from app.routes.jobs import router as jobs_router
# from app.routes.agent_routes import router as agent_router

app = FastAPI(
    title="JobPilot AI",
    description="Backend services for JobPilot AI",
    version="0.1.0"
)

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(job_search_router)
app.include_router(resume_agent_router)
app.include_router(resume_agent_v2_router)
# app.include_router(jobs_router)
# app.include_router(agent_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to JobPilot AI API"}
