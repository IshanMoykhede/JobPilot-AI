from pydantic import BaseModel, Field

class JobKnowledge(BaseModel):
    # -----------------------------
    # Basic Information
    # -----------------------------
    job_title: str = Field(description="Official title of the job.")
    company_name: str = Field(description="Name of the Company offering the job.")
    location: str | None = Field(default=None, description="Primary job location.")
    work_mode: str | None = Field(default=None, description="Remote, Hybrid or Onsite. ")
    employment_type: str | None = Field(default=None, description="Full Time, Internship, Contract, Part Time etc.")

    # -----------------------------
    # Experience
    # -----------------------------
    employment_level: str | None = Field(default=None, description="Intern, Junior, Mid, Senior, Lead etc.")
    minimum_experience_years: int | None = Field(default=None, description="Minimum years of experience required .")
    preferred_experience_years: int | None = Field(default=None, description="Preferred years of experience.")

    # -----------------------------
    # Education
    # -----------------------------
    required_degrees: list[str] = Field(default_factory=list, description="Mandatory educational degrees.")
    preferred_degrees: list[str] = Field(default_factory=list, description="Preferred educational degrees.")
    required_specializations: list[str] = Field(default_factory=list, description="Mandatory specializations.")
    preferred_specializations: list[str] = Field(default_factory=list, description="Preferred specializations.")

    # -----------------------------
    # Domain
    # -----------------------------
    primary_domain: str | None = Field(default=None, description="Primary engineering domain.")
    secondary_domains: list[str] = Field(default_factory=list, description="Additional engineering domains.")

    # -----------------------------
    # Skills
    # -----------------------------
    required_technologies: list[str] = Field(default_factory=list, description="Technologies explicitly required.")
    preferred_technologies: list[str] = Field(default_factory=list, description="Technologies that are preferred.")
    required_capabilities: list[str] = Field(default_factory=list, description="Mandatory capabilities.")
    preferred_capabilities: list[str] = Field(default_factory=list, description="Preferred capabilities.")
    required_certifications: list[str] = Field(default_factory=list, description="Mandatory certifications.")
    preferred_certifications: list[str] = Field(default_factory=list, description="Preferred certifications.")

    # -----------------------------
    # Job Details
    # -----------------------------
    responsibilities: list[str] = Field(default_factory=list, description="Key responsibilities of the role.")
    benefits: list[str] = Field(default_factory=list, description="Benefits offered by the employer.")
    salary_information: str | None = Field(default=None, description="Salary or compensation information if available.")
    industry: str | None = Field(default=None, description="Industry of the hiring company.")

class JobKnowledgeBatch(BaseModel):
    jobs: list[JobKnowledge]
