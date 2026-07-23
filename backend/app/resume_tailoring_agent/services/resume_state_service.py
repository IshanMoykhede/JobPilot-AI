import json
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.candidate_profile import CandidateProfile
from app.resume_tailoring_agent.state import ResumeAgentState
from app.resume_tailoring_agent.schemas.messaging import ResumeMessage, MessageRole, MessageType, MessageSource
from app.resume_tailoring_agent.schemas.common import ResumeContent, ResumeSection, ResumeSectionType, ResumeSectionState
from app.resume_tailoring_agent.schemas.personal_information import PersonalInformation
from app.models.user import User

class ResumeStateService:
    """
    Factory for constructing the initial ResumeAgentState and hydrating candidate intelligence.
    """
    def __init__(self, db: Session):
        self.db = db

    def _hydrate_candidate_intelligence(self, user_id: str) -> str:
        """
        Queries the database to gather all candidate data (skills, projects, education, insights)
        and formats it into the static candidate_synthesis string for the graph context.
        """
        profile = self.db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()
        if not profile:
            return ""

        synthesis_parts = []
        
        # 1. Base Intelligence (Skipped for V1 scope)
        # We are intentionally ignoring the large CANDIDATE_KNOWLEDGE insight JSON for V1.
        # It will be redesigned in V2.


        # 2. Extract Data from Profile JSON
        # For V1, we just return the entire profile_json as a string so that each
        # generator node can parse it and extract only the section they need.
        if profile.profile_json:
            return json.dumps(profile.profile_json)
        
        return "{}"

    def create_initial_state(self, user: User, resume_id: str, user_query: str, target_job_description: str) -> ResumeAgentState:
        """
        Creates the genesis state for a new resume generation graph execution.
        """
        candidate_synthesis = self._hydrate_candidate_intelligence(str(user.id))
        
        initial_msg = ResumeMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            role=MessageRole.USER,
            message_type=MessageType.USER_QUERY,
            from_node=MessageSource.USER,
            to_node=MessageSource.INTENT_ROUTER,
            content=user_query if user_query else "Please generate my complete resume."
        )
        
        # Try to extract phone/linkedin from profile_json if available
        phone = None
        linkedin = None
        location = None
        profile = self.db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
        if profile and profile.profile_json:
            pers_info = profile.profile_json.get("personal_information", {})
            if isinstance(pers_info, dict):
                phone = pers_info.get("phone")
                linkedin = pers_info.get("linkedin")
                location = pers_info.get("location")
                
        personal_info_section = ResumeSection(
            section_type=ResumeSectionType.PERSONAL_INFORMATION,
            display_name="Personal Information",
            status=ResumeSectionState.COMPLETED,
            content=PersonalInformation(
                full_name=user.name,
                email=user.email,
                phone=phone,
                location=location,
                linkedin=linkedin
            )
        )
        
        return ResumeAgentState(
            resume_id=resume_id,
            session_id=str(uuid.uuid4()),
            user_id=str(user.id),
            messages=[initial_msg],
            resume_content=ResumeContent(sections=[personal_info_section]),
            candidate_synthesis=candidate_synthesis,
            job_knowledge=target_job_description,
            pending_sections=[
                ResumeSectionType.SUMMARY,
                ResumeSectionType.PROJECTS,
                ResumeSectionType.EXPERIENCE,
                ResumeSectionType.SKILLS,
                ResumeSectionType.EDUCATION,
                ResumeSectionType.CERTIFICATIONS,
            ],
            current_section=None
        )
