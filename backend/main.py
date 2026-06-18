from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import router as auth_router
from app.routes.candidate_profile import router as profile_router

app = FastAPI(
    title="JobPilot AI API",
    description="Backend API for JobPilot AI - Authentication & Authorization Phase",
    version="1.0.0"
)

# Configure CORS for communication with the React frontend
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

@app.get("/")
def read_root():
    return {"message": "Welcome to JobPilot AI API"}
