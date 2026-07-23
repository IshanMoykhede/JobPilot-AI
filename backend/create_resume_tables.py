import sys
import os
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import Base, engine
# Import all models so they register with Base
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_insights import CandidateInsights
from app.job_search_agent.models.job_searches import JobSearch
from app.job_search_agent.models.job_knowledge import JobKnowledge
from app.job_search_agent.models.job_match_scores import JobMatchScore
from app.conversation.models.conversation import Conversation
from app.conversation.models.conversation_message import ConversationMessage
from app.models.otp import OTPVerification
from app.models.resume import Resume, ResumeMessageModel, ResumeContentModel

print("Creating missing tables...")
Base.metadata.create_all(bind=engine)
print("Done!")
