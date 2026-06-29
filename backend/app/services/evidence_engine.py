import logging
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session

from app.schemas.candidate_profile import CandidateProfileData, ExperienceSchema
from app.schemas.evidence import (
    CandidateEvidence, CandidateLevel, CandidateMaturity, EvidenceSummary
)
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_insights import CandidateInsights, InsightStatus

logger = logging.getLogger(__name__)

class EvidenceEngineService:
    """
    Deterministic business logic component responsible only for computing 
    candidate metadata (Level and Maturity).
    """

    @staticmethod
    def build_candidate_evidence(profile_data: CandidateProfileData, project_intelligence_list=None) -> CandidateEvidence:
        """
        Calculates minimal, deterministic candidate metadata.
        """
        candidate_resume = profile_data.resume_data
        
        candidate_level = EvidenceEngineService._calculate_candidate_level(candidate_resume.experience)
        candidate_maturity = EvidenceEngineService._calculate_candidate_maturity(candidate_resume)
        
        return CandidateEvidence(
            candidate_level=candidate_level,
            candidate_maturity=candidate_maturity,
            evidence_summary=EvidenceSummary()  # Defaults to 0/empty
        )

    @staticmethod
    def persist_evidence(db: Session, profile: CandidateProfile, evidence: CandidateEvidence) -> CandidateInsights:
        """
        Saves calculated evidence into the PostgreSQL database.
        """
        if profile.insights:
            insight = CandidateInsights(
                candidate_profile_id=profile.id,
                status=InsightStatus.COMPLETED,
                generated_at=datetime.utcnow()
            )
            db.add(insight)
        else:
            insight = CandidateInsights(
                candidate_profile_id=profile.id,
                status=InsightStatus.COMPLETED,
                generated_at=datetime.utcnow()
            )
            db.add(insight)
        
        current_json = insight.insights_json or {}
        current_json["evidence_engine"] = evidence.model_dump()
        insight.insights_json = current_json
        
        db.commit()
        db.refresh(insight)
        
        return insight

    @staticmethod
    def _calculate_candidate_level(experience_list: List[ExperienceSchema]) -> CandidateLevel:
        """
        Calculates total working months to classify Fresher, Junior, Mid-Level, or Senior.
        """
        total_months_worked = 0
        current_date = datetime.now()
        
        for job in experience_list:
            if not job.start_date: 
                continue
            
            try:
                start_parts = job.start_date.split("-")
                start_year = int(start_parts[0])
                start_month = int(start_parts[1]) if len(start_parts) > 1 else 1
                start_datetime = datetime(start_year, start_month, 1)
                
                end_datetime = current_date
                if job.end_date and job.end_date.lower() != "present":
                    end_parts = job.end_date.split("-")
                    end_year = int(end_parts[0])
                    end_month = int(end_parts[1]) if len(end_parts) > 1 else 1
                    end_datetime = datetime(end_year, end_month, 1)
                
                months = (end_datetime.year - start_datetime.year) * 12 + (end_datetime.month - start_datetime.month)
                
                if months > 0:
                    total_months_worked += months
                    
            except Exception:
                pass 
                
        if total_months_worked < 18: 
            title = "Fresher"
        elif total_months_worked < 36: 
            title = "Junior"
        elif total_months_worked < 84: 
            title = "Mid-Level"
        else: 
            title = "Senior"
        
        return CandidateLevel(title=title, total_months_experience=total_months_worked)

    @staticmethod
    def _calculate_candidate_maturity(resume) -> CandidateMaturity:
        """
        Calculates signs of candidate maturity/hustle based on raw resume counts.
        """
        total_internships = 0
        
        for job in resume.experience:
            if job.role and "intern" in job.role.lower():
                total_internships += 1
                
        return CandidateMaturity(
            project_count=len(resume.projects),
            certification_count=len(resume.certifications),
            internship_count=total_internships
        )
