import logging
from typing import Tuple
from app.job_search_agent.matching.core import matching_config
from app.job_search_agent.matching.schemas.comparison import (
    LLMComparisonResult, ScoreBreakdown, MatchStatus, ExperienceStatus,
    EducationStatus, DomainStatus
)

logger = logging.getLogger(__name__)

class DeterministicMatcher:
    @staticmethod
    def calculate_component_scores(llm_result: LLMComparisonResult) -> ScoreBreakdown:
        """
        Consumes the LLM's structured JSON categorization and applies strict numerical weights.
        The LLM identifies WHAT matches; this engine determines HOW MUCH it is worth.
        """
        
        # 1. Technology Score (Max: matching_config.TECH_WEIGHT)
        tech_score = 0.0
        tech_weight = matching_config.TECH_WEIGHT
        req_tech_count = len(llm_result.matched_required_technologies) + len(llm_result.missing_required_technologies) + len(llm_result.partial_required_technologies)
        if req_tech_count > 0:
            raw_req = len(llm_result.matched_required_technologies) + (len(llm_result.partial_required_technologies) * 0.5)
            req_percentage = raw_req / req_tech_count
            tech_score += (req_percentage * tech_weight * 0.8)
        else:
            tech_score += (tech_weight * 0.8)
            
        pref_tech_count = len(llm_result.matched_preferred_technologies) + len(llm_result.missing_preferred_technologies) + len(llm_result.partial_preferred_technologies)
        if pref_tech_count > 0:
            raw_pref = len(llm_result.matched_preferred_technologies) + (len(llm_result.partial_preferred_technologies) * 0.5)
            pref_percentage = raw_pref / pref_tech_count
            tech_score += (pref_percentage * tech_weight * 0.2)
        else:
            tech_score += (tech_weight * 0.2)
            
        tech_percentage = (tech_score / tech_weight * 100.0) if tech_weight > 0 else 100.0

        # 2. Capability Score (Max: matching_config.CAPABILITY_WEIGHT)
        cap_score = 0.0
        cap_weight = matching_config.CAPABILITY_WEIGHT
        req_cap_count = len(llm_result.matched_required_capabilities) + len(llm_result.missing_required_capabilities) + len(llm_result.partial_required_capabilities)
        if req_cap_count > 0:
            raw_req = len(llm_result.matched_required_capabilities) + (len(llm_result.partial_required_capabilities) * 0.5)
            req_percentage = raw_req / req_cap_count
            cap_score += (req_percentage * cap_weight * 0.8)
        else:
            cap_score += (cap_weight * 0.8)
            
        pref_cap_count = len(llm_result.matched_preferred_capabilities) + len(llm_result.missing_preferred_capabilities) + len(llm_result.partial_preferred_capabilities)
        if pref_cap_count > 0:
            raw_pref = len(llm_result.matched_preferred_capabilities) + (len(llm_result.partial_preferred_capabilities) * 0.5)
            pref_percentage = raw_pref / pref_cap_count
            cap_score += (pref_percentage * cap_weight * 0.2)
        else:
            cap_score += (cap_weight * 0.2)
            
        cap_percentage = (cap_score / cap_weight * 100.0) if cap_weight > 0 else 100.0

        # 3. Experience Score (Max: matching_config.LEVEL_WEIGHT)
        exp_score = 0.0
        exp_weight = matching_config.LEVEL_WEIGHT
        exp_status = llm_result.experience_comparison.status
        if exp_status == ExperienceStatus.MEETS_PREFERRED:
            exp_score = exp_weight
        elif exp_status == ExperienceStatus.MEETS_MINIMUM:
            exp_score = exp_weight * 0.8
        elif exp_status == ExperienceStatus.FALLS_SHORT_BUT_CLOSE:
            exp_score = exp_weight * 0.5
        else:
            exp_score = 0.0
            
        exp_percentage = (exp_score / exp_weight * 100.0) if exp_weight > 0 else 100.0

        # 4. Education Score (Arbitrary weight 5 for now)
        edu_score = 0.0
        edu_weight = 5.0
        edu_status = llm_result.education_comparison.degree_match
        if edu_status == EducationStatus.MEETS_PREFERRED:
            edu_score = edu_weight
        elif edu_status == EducationStatus.MEETS_REQUIRED:
            edu_score = edu_weight * 0.8
        
        # Bonus for specialization
        if llm_result.education_comparison.specialization_match == MatchStatus.MATCHED:
            edu_score += 2.0
            
        edu_percentage = min(100.0, (edu_score / edu_weight * 100.0)) if edu_weight > 0 else 100.0
            
        # 5. Certification Score (Arbitrary weight 3 for now)
        cert_score = 0.0
        cert_weight = 3.0
        if len(llm_result.certification_comparison.matched_required) > 0:
            cert_score += 3.0
        if len(llm_result.certification_comparison.matched_preferred) > 0:
            cert_score += 1.0
            
        cert_percentage = min(100.0, (cert_score / cert_weight * 100.0)) if cert_weight > 0 else 100.0
            
        # 6. Domain Score (Max: matching_config.DOMAIN_WEIGHT)
        dom_score = 0.0
        dom_weight = matching_config.DOMAIN_WEIGHT
        dom_status = llm_result.domain_comparison.status
        if dom_status == DomainStatus.PRIMARY_MATCH:
            dom_score = dom_weight
        elif dom_status == DomainStatus.SECONDARY_OVERLAP:
            dom_score = dom_weight * 0.6
        else:
            dom_score = 0.0
            
        dom_percentage = (dom_score / dom_weight * 100.0) if dom_weight > 0 else 100.0

        return ScoreBreakdown(
            technology=ScoreComponent(score=tech_score, weight=tech_weight, percentage=tech_percentage),
            capability=ScoreComponent(score=cap_score, weight=cap_weight, percentage=cap_percentage),
            experience=ScoreComponent(score=exp_score, weight=exp_weight, percentage=exp_percentage),
            education=ScoreComponent(score=edu_score, weight=edu_weight, percentage=edu_percentage),
            certification=ScoreComponent(score=cert_score, weight=cert_weight, percentage=cert_percentage),
            domain=ScoreComponent(score=dom_score, weight=dom_weight, percentage=dom_percentage)
        )

    @staticmethod
    def calculate_total_deterministic_score(breakdown: ScoreBreakdown) -> float:
        """Sums up the component scores, bounding it at 100."""
        total = (breakdown.technology.score + 
                 breakdown.capability.score + 
                 breakdown.experience.score + 
                 breakdown.education.score + 
                 breakdown.certification.score + 
                 breakdown.domain.score)
        
        return min(100.0, max(0.0, total))
