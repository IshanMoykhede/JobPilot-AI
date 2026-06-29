from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
import asyncio
from datetime import datetime, timezone
import logging

from app.schemas.candidate_profile import CandidateProfileData
from app.schemas.evidence import CandidateKnowledge
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_insights import CandidateInsights, InsightStatus, ArtifactType
from app.services.evidence_engine import EvidenceEngineService
from app.services.project_intelligence import ProjectIntelligenceService
from app.services.experience_intelligence import ExperienceIntelligenceService
from app.services.academic_intelligence import AcademicIntelligenceService
from app.services.knowledge_fusion import KnowledgeFusionService
from app.services.evidence_engine_v2 import EvidenceEngineV2
from app.core.evaluation_strategy import DefaultEvaluationStrategy
from app.services.candidate_synthesizer import CandidateSynthesizerService
from app.schemas.evidence import CandidateSynthesisInput

logger = logging.getLogger(__name__)

class CandidateKnowledgeEngine:
    """
    Orchestration service for the Candidate Knowledge Engine.
    Handles the generation, self-healing, and persistence of the CANDIDATE_KNOWLEDGE artifact.
    """

    @staticmethod
    async def ensure_candidate_knowledge(db: Session, profile: CandidateProfile) -> CandidateInsights:
        """
        Ensures that a valid CANDIDATE_KNOWLEDGE artifact exists and is up to date.
        If missing or STALE, it regenerates it synchronously.
        """
        insight = db.query(CandidateInsights).filter(
            CandidateInsights.candidate_profile_id == profile.id,
            CandidateInsights.artifact_type == ArtifactType.CANDIDATE_KNOWLEDGE
        ).order_by(CandidateInsights.created_at.desc()).first()

        # Check if missing or needs regeneration
        needs_regeneration = False
        if not insight:
            needs_regeneration = True
        elif insight.status in [InsightStatus.STALE, InsightStatus.FAILED]:  # type: ignore
            needs_regeneration = True
        else:
            # Check timestamps to be absolutely sure
            profile_updated = profile.updated_at
            if profile_updated and profile_updated.tzinfo is None:
                profile_updated = profile_updated.replace(tzinfo=timezone.utc)
            
            insight_generated = insight.generated_at  # type: ignore
            if insight_generated and insight_generated.tzinfo is None:
                insight_generated = insight_generated.replace(tzinfo=timezone.utc)
            
            if profile_updated and insight_generated and profile_updated > insight_generated:
                needs_regeneration = True

        if needs_regeneration:
            logger.info(f"Regenerating Candidate Knowledge for profile {profile.id}")
            insight = await CandidateKnowledgeEngine.generate_and_persist(db, profile)
            db.commit()
            db.refresh(insight)

        return insight

    @staticmethod
    async def generate_and_persist(db: Session, profile: CandidateProfile) -> CandidateInsights:
        """
        Forces generation of the CANDIDATE_KNOWLEDGE artifact.
        """
        if not profile.profile_json:
            raise ValueError("Cannot generate knowledge for an empty profile.")

        try:
            profile_req = CandidateProfileData(**profile.profile_json)
        except Exception as e:
            raise ValueError(f"Invalid profile format in database: {e}")

        # 1. LLM extraction (concurrently)
        projects = profile_req.resume_data.projects
        experience = profile_req.resume_data.experience
        education = profile_req.resume_data.education
        certifications = profile_req.resume_data.certifications
        
        project_intel, exp_intel, edu_intel, cert_intel = await asyncio.gather(
            ProjectIntelligenceService.analyze_projects(projects),
            ExperienceIntelligenceService.analyze_experiences(experience),
            AcademicIntelligenceService.analyze_education(education),
            AcademicIntelligenceService.analyze_certifications(certifications)
        )

        # 2. Extract Knowledge Fusion (LLM-powered semantic synthesis)
        unified_knowledge = await KnowledgeFusionService.fuse_knowledge(
            skills=profile_req.resume_data.skills,
            project_intel=project_intel,
            exp_intel=exp_intel,
            edu_intel=edu_intel,
            cert_intel=cert_intel
        )

        # 3. Generate legacy evidence (sync)
        # We pass project_intel so the old evidence engine still functions for backward compatibility
        evidence = EvidenceEngineService.build_candidate_evidence(profile_req, project_intel)
        
        # 4. Evaluate Candidate Knowledge (Evidence Engine V2)
        strategy = DefaultEvaluationStrategy()
        evidence_report = EvidenceEngineV2.evaluate(unified_knowledge, strategy)
        
        # 5. Synthesize Candidate Identity (Candidate Synthesizer)
        synthesis_input = CandidateSynthesisInput(
            unified_knowledge=unified_knowledge,
            evidence_report=evidence_report,
            project_intelligence=project_intel,
            experience_intelligence=exp_intel,
            education_intelligence=edu_intel,
            certification_intelligence=cert_intel
        )
        
        synthesizer = CandidateSynthesizerService()
        candidate_identity = await synthesizer.synthesize(synthesis_input)
        
        # 6. Assemble the top-level CandidateKnowledge artifact
        candidate_knowledge = CandidateKnowledge(
            candidate_level=evidence.candidate_level,
            candidate_maturity=evidence.candidate_maturity,
            unified_knowledge=unified_knowledge,
            evidence_report=evidence_report,
            candidate_identity=candidate_identity,
            project_intelligence=project_intel,
            experience_intelligence=exp_intel,
            education_intelligence=edu_intel,
            certification_intelligence=cert_intel
        )

        
        # 4. Package as a Knowledge Artifact
        artifact_data = candidate_knowledge.model_dump(mode="json")
        generated_now = datetime.now(timezone.utc)

        # 3. Upsert into CandidateInsights
        insight = db.query(CandidateInsights).filter(
            CandidateInsights.candidate_profile_id == profile.id,  # type: ignore
            CandidateInsights.artifact_type == ArtifactType.CANDIDATE_KNOWLEDGE  # type: ignore
        ).order_by(CandidateInsights.created_at.desc()).first()

        if insight:
            insight.artifact_json = artifact_data  # type: ignore
            insight.status = InsightStatus.COMPLETED  # type: ignore
            insight.generated_at = generated_now  # type: ignore
            flag_modified(insight, "artifact_json")
        else:
            insight = CandidateInsights(
                candidate_profile_id=profile.id,
                artifact_type=ArtifactType.CANDIDATE_KNOWLEDGE,
                artifact_json=artifact_data,
                status=InsightStatus.COMPLETED,
                generated_at=generated_now
            )
            db.add(insight)

        db.flush()
        db.refresh(insight)

        return insight

    @staticmethod
    def mark_knowledge_stale(db: Session, profile: CandidateProfile):
        """
        Marks the existing CANDIDATE_KNOWLEDGE artifact as STALE when profile data updates.
        """
        insight = db.query(CandidateInsights).filter(
            CandidateInsights.candidate_profile_id == profile.id,
            CandidateInsights.artifact_type == ArtifactType.CANDIDATE_KNOWLEDGE
        ).order_by(CandidateInsights.created_at.desc()).first()

        if insight and insight.status == InsightStatus.COMPLETED:
            insight.status = InsightStatus.STALE
            db.flush()
