from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class CandidateLevel(BaseModel):
    title: str = Field(description="Fresher, Junior, Mid-Level, Senior")
    total_months_experience: int

class CandidateMaturity(BaseModel):
    project_count: int = 0
    certification_count: int = 0
    internship_count: int = 0

class SkillEvidenceItem(BaseModel):
    total_score: int
    tier: str = Field(description="Claimed, Applied, Demonstrated")
    sources: List[str] = Field(default_factory=list)

class DomainClassification(BaseModel):
    current_domains: List[str] = Field(default_factory=list)
    target_domains: List[str] = Field(default_factory=list)

class EvidenceSummary(BaseModel):
    total_skills_detected: int = 0
    demonstrated_skills_count: int = 0
    claimed_only_skills_count: int = 0

class CandidateEvidence(BaseModel):
    candidate_level: CandidateLevel
    candidate_maturity: CandidateMaturity
    current_domains: List[str] = Field(default_factory=list)
    target_domains: List[str] = Field(default_factory=list)
    skill_evidence: Dict[str, SkillEvidenceItem] = Field(default_factory=dict)
    evidence_summary: EvidenceSummary
    project_complexity: Optional[str] = Field(default=None, description="Placeholder for future LLM scoring")
