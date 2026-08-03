from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class MatchStatus(str, Enum):
    MATCHED = "MATCHED"
    MISSING = "MISSING"
    PARTIAL = "PARTIAL"

class ExperienceStatus(str, Enum):
    MEETS_PREFERRED = "MEETS_PREFERRED"
    MEETS_MINIMUM = "MEETS_MINIMUM"
    FALLS_SHORT_BUT_CLOSE = "FALLS_SHORT_BUT_CLOSE"
    INSUFFICIENT = "INSUFFICIENT"

class EducationStatus(str, Enum):
    MEETS_PREFERRED = "MEETS_PREFERRED"
    MEETS_REQUIRED = "MEETS_REQUIRED"
    INSUFFICIENT = "INSUFFICIENT"

class DomainStatus(str, Enum):
    PRIMARY_MATCH = "PRIMARY_MATCH"
    SECONDARY_OVERLAP = "SECONDARY_OVERLAP"
    NO_MATCH = "NO_MATCH"

class SemanticMatch(BaseModel):
    job_requirement: str
    candidate_skill: Optional[str] = None
    match_type: str # 'exact', 'equivalent', 'partial', 'missing'

class ExperienceComparison(BaseModel):
    candidate_value: int
    required_value: int
    preferred_value: Optional[int] = None
    status: ExperienceStatus

class EducationComparison(BaseModel):
    degree_match: EducationStatus
    specialization_match: MatchStatus
    missing_required_degrees: List[str] = Field(default_factory=list)

class CertificationComparison(BaseModel):
    matched_required: List[SemanticMatch] = Field(default_factory=list)
    missing_required: List[str] = Field(default_factory=list)
    matched_preferred: List[SemanticMatch] = Field(default_factory=list)
    missing_preferred: List[str] = Field(default_factory=list)

class DomainComparison(BaseModel):
    status: DomainStatus
    matched_domains: List[str] = Field(default_factory=list)

class LLMComparisonResult(BaseModel):
    """Structured output expected from the LLM Phase 2"""
    matched_required_technologies: List[SemanticMatch] = Field(default_factory=list)
    missing_required_technologies: List[str] = Field(default_factory=list)
    partial_required_technologies: List[SemanticMatch] = Field(default_factory=list)
    
    matched_preferred_technologies: List[SemanticMatch] = Field(default_factory=list)
    missing_preferred_technologies: List[str] = Field(default_factory=list)
    partial_preferred_technologies: List[SemanticMatch] = Field(default_factory=list)
    
    matched_required_capabilities: List[SemanticMatch] = Field(default_factory=list)
    missing_required_capabilities: List[str] = Field(default_factory=list)
    partial_required_capabilities: List[SemanticMatch] = Field(default_factory=list)
    
    matched_preferred_capabilities: List[SemanticMatch] = Field(default_factory=list)
    missing_preferred_capabilities: List[str] = Field(default_factory=list)
    partial_preferred_capabilities: List[SemanticMatch] = Field(default_factory=list)
    
    experience_comparison: ExperienceComparison
    education_comparison: EducationComparison
    certification_comparison: CertificationComparison
    domain_comparison: DomainComparison

class ScoreComponent(BaseModel):
    score: float
    weight: float
    percentage: float

class ScoreBreakdown(BaseModel):
    technology: ScoreComponent
    capability: ScoreComponent
    experience: ScoreComponent
    education: ScoreComponent
    certification: ScoreComponent
    domain: ScoreComponent

class CandidateContext(BaseModel):
    level: str
    primary_domain: str
    total_experience_months: int

class MatchKnowledge(BaseModel):
    """The final persisted object produced by Pipeline 4 Phase 3"""
    match_schema_version: str = "v1"
    candidate_context: CandidateContext
    semantic_score: float
    structured_comparison: LLMComparisonResult
    component_scores: ScoreBreakdown
    final_score: float

class JobMatchResult(BaseModel):
    job_id: str
    comparison: LLMComparisonResult

class BatchLLMComparisonResult(BaseModel):
    matches: List[JobMatchResult]
