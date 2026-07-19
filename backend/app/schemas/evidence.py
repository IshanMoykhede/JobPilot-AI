from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Literal
from enum import Enum

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

class ComplexityLevel(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    PRODUCTION = "PRODUCTION"



class EngineeringDomain(str, Enum):
    SOFTWARE_ENGINEERING = "Software Engineering"
    AI_MACHINE_LEARNING = "Artificial Intelligence / Machine Learning"
    DATA_SCIENCE = "Data Science"
    CYBER_SECURITY = "Cyber Security"
    CLOUD_COMPUTING = "Cloud Computing"
    DEVOPS = "DevOps"
    MECHANICAL_ENGINEERING = "Mechanical Engineering"
    CIVIL_ENGINEERING = "Civil Engineering"
    CHEMICAL_ENGINEERING = "Chemical Engineering"
    ELECTRICAL_ENGINEERING = "Electrical Engineering"
    ELECTRONICS_ENGINEERING = "Electronics Engineering"
    EMBEDDED_SYSTEMS = "Embedded Systems"
    UNKNOWN_ENGINEERING_DOMAIN = "Unknown Engineering Domain"

class WorkType(str, Enum):
    PROJECT = "PROJECT"
    EXPERIENCE = "EXPERIENCE"
    INTERNSHIP = "INTERNSHIP"
    OPEN_SOURCE = "OPEN_SOURCE"

class KnowledgeDomain(BaseModel):
    primary_domain: EngineeringDomain
    secondary_domains: List[EngineeringDomain]

class EngineeringCapability(str, Enum):
    BACKEND_DEVELOPMENT = "Backend Development"
    FRONTEND_DEVELOPMENT = "Frontend Development"
    REST_API_DESIGN = "REST API Design"
    AUTHENTICATION = "Authentication"
    AUTHORIZATION = "Authorization"
    AGENTIC_WORKFLOWS = "Agentic Workflows"
    PROMPT_ENGINEERING = "Prompt Engineering"
    AI_API_INTEGRATION = "AI API Integration"
    DATABASE_DESIGN = "Database Design"
    DEPLOYMENT = "Deployment"
    CONTAINERIZATION = "Containerization"
    CI_CD = "CI/CD"
    SYSTEM_ARCHITECTURE = "System Architecture"
    PERFORMANCE_OPTIMIZATION = "Performance Optimization"
    PAYMENT_INTEGRATION = "Payment Integration"
    REAL_TIME_SYSTEMS = "Real-time Systems"
    
    # Mechanical Engineering
    THERMODYNAMICS_DESIGN = "Thermodynamics Design"
    FINITE_ELEMENT_ANALYSIS = "Finite Element Analysis"
    CAD_MODELING = "CAD Modeling"
    ROBOTICS_DESIGN = "Robotics Design"
    
    # Electrical/Electronics Engineering
    PCB_DESIGN = "PCB Design"
    EMBEDDED_SYSTEMS_PROGRAMMING = "Embedded Systems Programming"
    POWER_SYSTEMS_DESIGN = "Power Systems Design"
    
    # Civil Engineering
    STRUCTURAL_ENGINEERING = "Structural Engineering"
    CONSTRUCTION_MANAGEMENT = "Construction Management"
    GEOTECHNICAL_ANALYSIS = "Geotechnical Analysis"
    
    # Chemical Engineering
    PROCESS_DESIGN = "Process Design"
    CHEMICAL_PROCESS_SCALING = "Chemical Process Scaling"
    FLUID_DYNAMICS_ANALYSIS = "Fluid Dynamics Analysis"
    
    # General / Cross-Domain
    PROJECT_MANAGEMENT = "Project Management"
    QUALITY_ASSURANCE = "Quality Assurance"

class StructuredAchievement(BaseModel):
    action: str                        # e.g., "Implemented", "Optimized"
    technologies: List[str]            # e.g., ["Redis"]
    problem: str                       # e.g., "Slow database queries"
    solution: str                      # e.g., "Redis cache"
    impact: Optional[str] = None       # e.g., "45% reduction"

class ProjectIntelligence(BaseModel):
    project_name: str
    project_type: str
    complexity: ComplexityLevel
    domains: List[EngineeringDomain]
    technologies: List[str]
    capabilities: List[str]
    achievements: List[StructuredAchievement]
    architecture_tags: List[str] = []

class ExperienceIntelligence(BaseModel):
    role: str
    company: str
    duration: str
    work_type: WorkType
    domains: List[EngineeringDomain]
    technologies: List[str]
    capabilities: List[str]
    achievements: List[StructuredAchievement]

class EducationIntelligence(BaseModel):
    degree: str
    university: str
    specialization: Optional[str] = None
    cgpa: Optional[float] = None
    graduation_year: Optional[int] = None

class CertificationIntelligence(BaseModel):
    certification_name: str
    issuing_organization: str
    completion_date: Optional[str] = None
    technologies: List[str] = []
    capabilities: List[str] = []

class SourceReference(BaseModel):
    source_type: str                   # "PROJECT", "EXPERIENCE", "EDUCATION", "CERTIFICATION"
    source_name: str                   # e.g., "CampusConnect", "Software Engineer @ Google"
    explicit: bool

class UnifiedKnowledgeItem(BaseModel):
    name: str
    category: Literal["TECHNOLOGY", "CAPABILITY"]
    evidence_status: EvidenceStatus
    source_evidence: List[SourceReference]

class UnifiedKnowledge(BaseModel):
    technologies: List[UnifiedKnowledgeItem]
    capabilities: List[UnifiedKnowledgeItem]

class EvidenceStatus(str, Enum):
    CLAIMED = "Claimed"
    DEMONSTRATED = "Demonstrated"
    STRONGLY_DEMONSTRATED = "Strongly Demonstrated"
    ACADEMIC = "Academic"
    PROFESSIONAL = "Professional"
    WEAK_EVIDENCE = "Weak Evidence"
    CONFLICTING = "Conflicting"

class EvidenceQuality(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class KnowledgeEvaluation(BaseModel):
    name: str
    category: Literal["TECHNOLOGY", "CAPABILITY"]
    confidence_score: int = Field(ge=0, le=100)
    occurrences: int = 1
    source_strength: int = Field(default=0, ge=0, le=100)
    evidence_diversity: int = Field(default=0, ge=0, le=100)
    practical_demonstration: int = Field(default=0, ge=0, le=100)
    academic_support: int = Field(default=0, ge=0, le=100)
    evidence_quality: EvidenceQuality
    evidence_status: EvidenceStatus
    reasoning: str

class CandidateEvidenceReport(BaseModel):
    evaluations: Dict[str, KnowledgeEvaluation]
    overall_strengths: List[str]
    overall_weaknesses: List[str]

class DomainStrength(BaseModel):
    domain: EngineeringDomain
    score: int = Field(ge=0, le=100)
    experience_months: int = 0
    evidence_count: int = 0
    supporting_projects: List[str] = Field(default_factory=list)
    supporting_experience: List[str] = Field(default_factory=list)

class EngineeringProfile(BaseModel):
    domain_strengths: List[DomainStrength]

class CandidateIdentity(BaseModel):
    primary_specialization: str
    secondary_specializations: List[str]
    engineering_domains: List[EngineeringDomain]
    technology_stack: List[str]
    strongest_capabilities: List[str]
    experience_level: str
    ideal_roles: List[str]

class SynthesizedSkill(BaseModel):
    name: str
    category: str      # "TECHNOLOGY" or "CAPABILITY"
    status: str        # "Demonstrated", "Claimed", "Academic", "Weak Evidence"
    confidence_score: int
    occurrences: int

class ProjectSummary(BaseModel):
    title: str
    complexity: str    # "BEGINNER", "INTERMEDIATE", "ADVANCED", "PRODUCTION"
    primary_domain: str
    technologies: List[str]
    capabilities: List[str]

class ExperienceSummary(BaseModel):
    role: str
    company: str
    work_type: str     # "EXPERIENCE" or "INTERNSHIP"
    complexity: str
    primary_domain: str
    technologies: List[str]
    capabilities: List[str]

class AcademicSummary(BaseModel):
    name: str          # Degree or certification name
    issuer: str        # University or issuing organization
    type: str          # "EDUCATION" or "CERTIFICATION"

class CandidateSynthesisInput(BaseModel):
    skills: List[SynthesizedSkill]
    projects: List[ProjectSummary]
    experiences: List[ExperienceSummary]
    academics: List[AcademicSummary]

class CandidateKnowledge(BaseModel):
    candidate_level: CandidateLevel
    candidate_maturity: CandidateMaturity
    unified_knowledge: UnifiedKnowledge
    evidence_report: CandidateEvidenceReport
    candidate_identity: CandidateIdentity
    engineering_profile: EngineeringProfile
    project_intelligence: List[ProjectIntelligence] = Field(default_factory=list)
    experience_intelligence: List[ExperienceIntelligence] = Field(default_factory=list)
    education_intelligence: List[EducationIntelligence] = Field(default_factory=list)
    certification_intelligence: List[CertificationIntelligence] = Field(default_factory=list)
