from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class DemandSignal(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class SkillMatchStatus(str, Enum):
    DEMONSTRATED = "DEMONSTRATED"
    CLAIMED = "CLAIMED"
    MISSING = "MISSING"

class Citation(BaseModel):
    """
    Flat listing of sources analyzed during research.
    """
    title: str = Field(description="Title of the source webpage or job posting.")
    url: str = Field(description="Source link URL.")

class SegmentedSkill(BaseModel):
    """
    Technical skills categorized with importance indicators, ranking, and match status.
    """
    name: str = Field(description="Name of the technology or framework (e.g. 'PostgreSQL', not 'Postgres').")
    demand_signal: DemandSignal = Field(description="Heuristic demand rating: HIGH, MEDIUM, or LOW.")
    rank: int = Field(description="Relative rank of importance within its category (e.g. 1 to 5).")
    why_this_matters: str = Field(description="Short 1-sentence explanation of why this is valued, max 1 sentence.")
    match_status: Optional[SkillMatchStatus] = Field(default=None, description="Lightweight match comparison with candidate evidence.")

class MarketIntelligence(BaseModel):
    """
    Structured data representing v2 market expectations, skill segmentations, and citations for a role.
    """
    role_name: str = Field(description="Name of the researched role, e.g. 'Junior AI Engineer'.")
    market_summary: str = Field(description="Recruiter-style observations for 2026 hiring expectations. Max 2 sentences.")
    must_have_skills: List[SegmentedSkill] = Field(description="Baseline critical technical skills (max 5 items).")
    strong_advantage_skills: List[SegmentedSkill] = Field(description="Differentiating nice-to-have skills (max 5 items).")
    emerging_skills: List[SegmentedSkill] = Field(description="Cutting edge or future trending technologies (max 5 items).")
    common_tools: List[SegmentedSkill] = Field(description="Specific tools and platforms (e.g. Docker, AWS, Databricks) (max 5 items).")
    core_responsibilities: List[str] = Field(description="Core tasks, architectures, and day-to-day requirements.")
    citations: List[Citation] = Field(description="Flat list of sources analyzed for this role.")
    analyzed_sources_count: int = Field(description="Count of analyzed job postings or source sites.")
    source_breakdown: Dict[str, int] = Field(default_factory=dict, description="Occurrences of key platforms like LinkedIn, Indeed, etc. extracted from citations.")
    generated_at: datetime = Field(description="The timestamp when this research snapshot was generated.")

class RecommendationLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class GapAnalysis(BaseModel):
    """
    Factual gap results comparing profile against market expectations.
    """
    strengths: List[str] = Field(description="Demonstrated technical skills.")
    weak_evidence: List[str] = Field(description="Claimed skills lacking project evidence.")
    missing_skills: List[str] = Field(description="Market expectations completely missing from candidate profile.")
    priority_gaps: List[str] = Field(description="Highest importance missing skills sorted by demand signal and rank.")

class Recommendation(BaseModel):
    """
    Level-appropriate action item for the candidate.
    """
    title: str = Field(description="Concise, action-oriented title (e.g. 'Build a RAG Application').")
    reason: str = Field(description="1-sentence explanation of why this matters for the target role.")
    action: str = Field(description="Detailed, concrete action step to implement the missing technologies.")
    impact: RecommendationLevel = Field(description="Career/hiring impact value.")
    effort: RecommendationLevel = Field(description="Estimated development effort value.")

class RecommendationResult(BaseModel):
    """
    Aggregated gap analysis and actionable recommendations for a specific role.
    """
    gap_analysis: GapAnalysis
    recommendations: List[Recommendation]

