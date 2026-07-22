from pydantic import BaseModel, Field

class JobEvaluation(BaseModel):
    job_id: str = Field(description="The internal job ID provided in the prompt.")
    
    # Technologies / Tools
    matching_tech: list[str] = Field(description="Technologies/tools the candidate has that the job requires.")
    missing_tech: list[str] = Field(description="Technologies/tools the job requires that the candidate lacks.")
    
    # Education & Experience & Domain
    matching_qualifications: list[str] = Field(description="Degrees, years of experience, or domains the candidate has matching the job.")
    missing_qualifications: list[str] = Field(description="Degrees, experience, or domains required but missing in the candidate.")
    
    # Responsibilities / Capabilities
    matching_capabilities: list[str] = Field(description="Job responsibilities or capabilities the candidate has proven experience with.")
    missing_capabilities: list[str] = Field(description="Job responsibilities the candidate has no evidence of handling.")

class JobEvaluationBatch(BaseModel):
    evaluations: list[JobEvaluation]
