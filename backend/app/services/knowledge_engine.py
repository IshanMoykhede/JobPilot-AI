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
from app.schemas.evidence import (
    CandidateKnowledge,
    CandidateSynthesisInput,
    SynthesizedSkill,
    ProjectSummary,
    ExperienceSummary,
    AcademicSummary
)

from app.services.candidate_synthesizer import CandidateSynthesizerService

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
        
        project_intel = await ProjectIntelligenceService.analyze_projects(projects)
        exp_intel = await ExperienceIntelligenceService.analyze_experiences(experience)
        edu_intel = await AcademicIntelligenceService.analyze_education(education)
        cert_intel = await AcademicIntelligenceService.analyze_certifications(certifications)

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
        skills_input = []
        for name, eval_obj in evidence_report.evaluations.items():
            category = eval_obj.category.value if hasattr(eval_obj.category, 'value') else str(eval_obj.category)
            status = eval_obj.evidence_status.value if hasattr(eval_obj.evidence_status, 'value') else str(eval_obj.evidence_status)
            skills_input.append(SynthesizedSkill(
                name=name,
                category=category,
                status=status,
                confidence_score=eval_obj.confidence_score,
                occurrences=eval_obj.occurrences
            ))

        projects_input = []
        for p in project_intel:
            primary_domain = p.domains[0].value if p.domains and hasattr(p.domains[0], 'value') else (str(p.domains[0]) if p.domains else "Software Engineering")
            complexity = p.complexity.value if hasattr(p.complexity, 'value') else str(p.complexity)
            projects_input.append(ProjectSummary(
                title=p.project_name,
                complexity=complexity,
                primary_domain=primary_domain,
                technologies=p.technologies or [],
                capabilities=p.capabilities or []
            ))

        experiences_input = []
        for e in exp_intel:
            primary_domain = e.domains[0].value if e.domains and hasattr(e.domains[0], 'value') else (str(e.domains[0]) if e.domains else "Software Engineering")
            work_type = e.work_type.value if hasattr(e.work_type, 'value') else str(e.work_type)
            experiences_input.append(ExperienceSummary(
                role=e.role,
                company=e.company,
                work_type=work_type,
                complexity="INTERMEDIATE",
                primary_domain=primary_domain,
                technologies=e.technologies or [],
                capabilities=e.capabilities or []
            ))

        academics_input = []
        for edu in edu_intel:
            edu_name = f"{edu.degree} in {edu.specialization}" if edu.specialization else edu.degree
            academics_input.append(AcademicSummary(
                name=edu_name,
                issuer=edu.university,
                type="EDUCATION"
            ))
        for cert in cert_intel:
            academics_input.append(AcademicSummary(
                name=cert.certification_name,
                issuer=cert.issuing_organization,
                type="CERTIFICATION"
            ))

        synthesis_input = CandidateSynthesisInput(
            skills=skills_input,
            projects=projects_input,
            experiences=experiences_input,
            academics=academics_input
        )
        
        synthesizer = CandidateSynthesizerService()
        candidate_identity = await synthesizer.synthesize(synthesis_input)
        
        # 5b. Compute explainable EngineeringProfile
        from app.schemas.evidence import EngineeringDomain, DomainStrength, EngineeringProfile
        import re
        from datetime import datetime

        def parse_duration_months(duration_str: str) -> int:
            try:
                months_map = {
                    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
                    "january": 1, "february": 2, "march": 3, "april": 4, "june": 6,
                    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
                }
                
                def parse_date(date_str: str):
                    date_str = date_str.strip().lower()
                    if not date_str or date_str in ["present", "current", "now"]:
                        return datetime.now()
                    match = re.search(r'([a-z]+)\s*(\d{4})', date_str)
                    if match:
                        m_str, y_str = match.groups()
                        m = months_map.get(m_str, 1)
                        y = int(y_str)
                        return datetime(y, m, 1)
                    match_yr = re.search(r'\d{4}', date_str)
                    if match_yr:
                        return datetime(int(match_yr.group()), 1, 1)
                    return datetime.now()
                    
                parts = re.split(r'[-–to]', duration_str)
                if len(parts) == 2:
                    start = parse_date(parts[0])
                    end = parse_date(parts[1])
                    diff = (end.year - start.year) * 12 + (end.month - start.month)
                    return max(1, diff)
            except Exception as e:
                logger.error(f"Error parsing duration '{duration_str}': {e}")
            return 6

        domain_strengths = []
        for domain in EngineeringDomain:
            supporting_projects = [p.project_name for p in project_intel if domain in p.domains]
            supporting_exp_titles = [f"{e.role} @ {e.company}" for e in exp_intel if domain in e.domains]
            evidence_count = len(supporting_projects) + len(supporting_exp_titles)
            
            if evidence_count == 0:
                continue
                
            total_months = 0
            for e in exp_intel:
                if domain in e.domains:
                    total_months += parse_duration_months(e.duration)
                    
            # Formula: base 40 + 15 points per evidence (cap 40) + 1.5 points per month (cap 20)
            score = min(100, 40 + min(40, evidence_count * 15) + min(20, int(total_months * 1.5)))
            
            domain_strengths.append(DomainStrength(
                domain=domain,
                score=score,
                experience_months=total_months,
                evidence_count=evidence_count,
                supporting_projects=supporting_projects,
                supporting_experience=supporting_exp_titles
            ))
            
        engineering_profile = EngineeringProfile(domain_strengths=domain_strengths)

        # 6. Assemble the top-level CandidateKnowledge artifact
        candidate_knowledge = CandidateKnowledge(
            candidate_level=evidence.candidate_level,
            candidate_maturity=evidence.candidate_maturity,
            unified_knowledge=unified_knowledge,
            evidence_report=evidence_report,
            candidate_identity=candidate_identity,
            engineering_profile=engineering_profile,
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

        # Generate Candidate Embedding
        from app.embedding.services.embedding_pipeline import EmbeddingGenerationPipeline
        await EmbeddingGenerationPipeline.generate_candidate_embedding(db, insight.id)

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
