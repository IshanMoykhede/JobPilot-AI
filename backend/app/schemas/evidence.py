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

class BaseIntelligence(BaseModel):
    display_name: str
    domain: KnowledgeDomain
    summary: str
    explicit_technologies: List[str] = Field(default_factory=list)
    engineering_capabilities: List[EngineeringCapability] = Field(default_factory=list)

class BaseWorkIntelligence(BaseIntelligence):
    work_type: WorkType
    complexity: ComplexityLevel

class ProjectIntelligence(BaseWorkIntelligence):
    work_type: WorkType = Field(default=WorkType.PROJECT)
    project_name: str
    project_type: str

class ExperienceIntelligence(BaseWorkIntelligence):
    work_type: WorkType = Field(default=WorkType.EXPERIENCE)
    company: str
    role: str
    responsibilities_performed: List[str] = Field(default_factory=list)

class AcademicType(str, Enum):
    EDUCATION = "EDUCATION"
    CERTIFICATION = "CERTIFICATION"
    COURSE = "COURSE"
    BOOTCAMP = "BOOTCAMP"

class BaseAcademicIntelligence(BaseIntelligence):
    academic_type: AcademicType

class EducationIntelligence(BaseAcademicIntelligence):
    academic_type: AcademicType = Field(default=AcademicType.EDUCATION)
    degree: str
    specialization: str
    university: str
    coursework: List[str] = Field(default_factory=list)
    projects_completed: List[str] = Field(default_factory=list)
    research_summary: Optional[str] = None

class CertificationIntelligence(BaseAcademicIntelligence):
    academic_type: AcademicType = Field(default=AcademicType.CERTIFICATION)
    certification_name: str
    issuing_organization: str
    completion_date: Optional[str] = None

class EvidenceReference(BaseModel):
    source_type: Literal[
        "SKILL",
        "PROJECT",
        "EXPERIENCE",
        "EDUCATION",
        "CERTIFICATION"
    ]
    source_name: str
    explicit: bool
    reasoning: Optional[str] = None

class KnowledgeItem(BaseModel):
    name: str
    category: Literal[
        "TECHNOLOGY",
        "CAPABILITY"
    ]
    occurrences: int
    evidence: List[EvidenceReference]

class UnifiedKnowledge(BaseModel):
    technologies: List[KnowledgeItem]
    capabilities: List[KnowledgeItem]

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
    
    # Internal Intermediate Dimensions
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

class CandidateIdentity(BaseModel):
    primary_specialization: str
    secondary_specializations: List[str]
    engineering_domains: List[EngineeringDomain]
    strongest_capabilities: List[EngineeringCapability]
    primary_technology_stack: List[str]
    supporting_technologies: List[str]
    engineering_profile: str
    ideal_roles: List[str]
    preferred_industries: List[str]
    recruiter_summary: str
    knowledge_reasoning: List[str] = Field(default_factory=list)

    @field_validator("engineering_domains", mode="before")
    @classmethod
    def validate_domains(cls, v):
        if not isinstance(v, list):
            return []
        valid_domains = []
        for item in v:
            matched = None
            if isinstance(item, str):
                cleaned = item.strip().lower()
                for domain in EngineeringDomain:
                    if domain.value.lower() == cleaned or domain.name.lower() == cleaned:
                        matched = domain
                        break
            elif isinstance(item, EngineeringDomain):
                matched = item
            if matched:
                valid_domains.append(matched)
        return valid_domains

    @field_validator("strongest_capabilities", mode="before")
    @classmethod
    def validate_capabilities(cls, v):
        if not isinstance(v, list):
            return []
        valid_caps = []
        for item in v:
            matched = None
            if isinstance(item, str):
                cleaned = item.strip().lower()
                for cap in EngineeringCapability:
                    if cap.value.lower() == cleaned or cap.name.lower() == cleaned:
                        matched = cap
                        break
            elif isinstance(item, EngineeringCapability):
                matched = item
            if matched:
                valid_caps.append(matched)
        return valid_caps

class CandidateSynthesisInput(BaseModel):
    unified_knowledge: UnifiedKnowledge
    evidence_report: CandidateEvidenceReport
    project_intelligence: List[ProjectIntelligence]
    experience_intelligence: List[ExperienceIntelligence]
    education_intelligence: List[EducationIntelligence]
    certification_intelligence: List[CertificationIntelligence]

class CandidateKnowledge(BaseModel):
    candidate_level: CandidateLevel
    candidate_maturity: CandidateMaturity
    unified_knowledge: UnifiedKnowledge
    evidence_report: CandidateEvidenceReport
    candidate_identity: CandidateIdentity
    project_intelligence: List[ProjectIntelligence] = Field(default_factory=list)
    experience_intelligence: List[ExperienceIntelligence] = Field(default_factory=list)
    education_intelligence: List[EducationIntelligence] = Field(default_factory=list)
    certification_intelligence: List[CertificationIntelligence] = Field(default_factory=list)
