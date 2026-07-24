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

        profile_data = profile.profile_json or {}
        
        # Query CandidateInsights (CANDIDATE_KNOWLEDGE)
        from app.models.candidate_insights import CandidateInsights, ArtifactType
        insight = self.db.query(CandidateInsights).filter(
            CandidateInsights.candidate_profile_id == profile.id,
            CandidateInsights.artifact_type == ArtifactType.CANDIDATE_KNOWLEDGE
        ).order_by(CandidateInsights.created_at.desc()).first()
        
        insights_data = insight.artifact_json if (insight and insight.artifact_json) else {}
        
        # Merge them into a unified structure
        synthesis = {
            "resume_data": profile_data.get("resume_data", profile_data),
            "onboarding_insights": insights_data
        }
        
        return json.dumps(synthesis)

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
            messages=[initial_msg.model_dump(mode="json")],
            resume_content=ResumeContent(sections=[personal_info_section]).model_dump(mode="json"),
            candidate_synthesis=candidate_synthesis,
            user_profile_data=json.dumps(profile.profile_json) if profile and profile.profile_json else None,
            job_knowledge=target_job_description,
            pending_sections=[
                ResumeSectionType.PROJECTS.value,
                ResumeSectionType.EXPERIENCE.value,
                ResumeSectionType.SKILLS.value,
                ResumeSectionType.EDUCATION.value,
                ResumeSectionType.CERTIFICATIONS.value,
                ResumeSectionType.CO_CURRICULAR.value,
                ResumeSectionType.SUMMARY.value,
            ],
            current_section=None
        )
