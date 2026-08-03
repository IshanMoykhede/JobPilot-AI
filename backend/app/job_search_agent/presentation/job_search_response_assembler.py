import logging
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.job_search.models.search_workspace import SearchWorkspace
from app.job_search.models.job_search_result import JobSearchResult
from app.job_search_agent.presentation.schemas.job_search import (
    JobSearchResponse,
    JobSearchPayloadDTO,
    SearchStatisticsDTO,
    JobCardResponse,
    JobMetadataDTO,
    JobMatchDTO,
    JobGuidanceDTO,
    JobActionsDTO
)

logger = logging.getLogger(__name__)

class JobSearchResponseAssembler:
    @staticmethod
    def build_job_card(db_job: JobSearchResult) -> JobCardResponse:
        """
        Assembles a JobSearchResult (including Pipeline 4 & 5 outputs) into a clean, 
        frontend-agnostic JobCardResponse DTO.
        """
        # --- Metadata Assembly ---
        metadata = JobMetadataDTO(
            title=db_job.job_title,
            company=db_job.company_name or "Unknown Company",
            location=db_job.location,
            work_mode=db_job.work_mode,
            apply_url=db_job.apply_url
        )

        # --- Match & Guidance Assembly ---
        # Parse CandidateGuidance JSON output from Pipeline 5
        guidance_dict = db_job.ai_explanation or {}
        score = db_job.final_score or 0.0
        
        # Deterministically assign UI attributes based on score
        if score >= 85:
            score_color = "text-jp-success"
            score_badge = "jp-badge-success"
            progress_variant = "success"
        elif score >= 70:
            score_color = "text-jp-accent"
            score_badge = "jp-badge-accent"
            progress_variant = "accent"
        elif score >= 50:
            score_color = "text-jp-warning"
            score_badge = "jp-badge-warning"
            progress_variant = "warning"
        else:
            score_color = "text-jp-error"
            score_badge = "jp-badge-error"
            progress_variant = "error"
        
        match_dto = JobMatchDTO(
            score=score,
            confidence=guidance_dict.get("confidence", "Medium"),
            application_decision=guidance_dict.get("application_decision", "Apply"),
            score_color=score_color,
            score_badge=score_badge,
            progress_variant=progress_variant
        )

        guidance_dto = JobGuidanceDTO(
            overall_fit=guidance_dict.get("overall_fit", "No detailed fit analysis available."),
            strengths=guidance_dict.get("strengths", []),
            skill_gaps=guidance_dict.get("skill_gaps", []),
            next_steps=guidance_dict.get("next_steps", []),
            resume_focus_areas=guidance_dict.get("resume_focus_areas", []),
            interview_focus_areas=guidance_dict.get("interview_focus_areas", []),
            experience_assessment=guidance_dict.get("experience_assessment", ""),
            education_assessment=guidance_dict.get("education_assessment", ""),
            application_reason=guidance_dict.get("application_reason", "")
        )

        # --- Actions Assembly ---
        actions_dto = JobActionsDTO(
            can_tailor_resume=True,
            can_prepare_interview=True,
            has_skill_gaps=len(guidance_dto.skill_gaps) > 0,
            has_resume_recommendations=len(guidance_dto.resume_focus_areas) > 0
        )

        return JobCardResponse(
            job_id=str(db_job.id),
            job=metadata,
            match=match_dto,
            guidance=guidance_dto,
            actions=actions_dto
        )

    @staticmethod
    def build_response(
        db: Session,
        workspace_id: uuid.UUID
    ) -> JobSearchResponse:
        """
        Builds the presentation API payload for all job search results in a workspace.
        """
        logger.info(f"[ResponseBuilder] Building presentation response for workspace: {workspace_id}")
        
        workspace = db.query(SearchWorkspace).filter(SearchWorkspace.id == workspace_id).first()
        if not workspace:
            logger.error(f"[ResponseBuilder] Workspace {workspace_id} not found")
            raise ValueError(f"Workspace {workspace_id} not found.")

        # Fetch all job results for this workspace that have scores
        job_results = db.query(JobSearchResult).filter(
            JobSearchResult.workspace_id == workspace_id,
            JobSearchResult.final_score.isnot(None)
        ).order_by(JobSearchResult.final_score.desc()).all()

        job_cards = []
        for db_job in job_results:
            try:
                card = JobSearchResponseAssembler.build_job_card(db_job)
                job_cards.append(card)
            except Exception as e:
                logger.error(f"[ResponseBuilder] Failed to assemble job {db_job.id}: {e}")

        # Calculate statistics
        total_jobs = workspace.total_jobs_fetched or len(job_results)
        top_matches = len(job_cards)
        scores = [card.match.score for card in job_cards] if job_cards else []
        avg_score = sum(scores) / len(scores) if scores else 0.0
        highest = max(scores) if scores else 0.0
        lowest = min(scores) if scores else 0.0
        
        logger.info(f"[ResponseBuilder] Presentation complete: {top_matches} job cards assembled.")

        statistics = SearchStatisticsDTO(
            total_jobs=total_jobs,
            top_matches=top_matches,
            average_match_score=round(avg_score, 1),
            highest_match_score=round(highest, 1),
            lowest_match_score=round(lowest, 1)
        )

        query_title = workspace.original_query.title() if workspace.original_query else "Job Search"

        payload = JobSearchPayloadDTO(
            query_title=query_title,
            statistics=statistics,
            jobs=job_cards
        )

        return JobSearchResponse(
            conversation_id=str(workspace.conversation_id),
            workspace_id=str(workspace.id),
            agent="job_search",
            payload=payload
        )