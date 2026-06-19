import sys
import os
import json

# Ensure the app module can be imported
sys.path.append(r"c:\Users\igmoy\OneDrive\Desktop\JobPilot AI\backend")

from app.schemas.candidate_profile import CompleteOnboardingRequest, ResumeDataSchema, ExperienceSchema, ProjectSchema, CertificationSchema, PreferencesSchema, ExperienceLevel, ResumeMetadataSchema
from app.services.evidence_engine import EvidenceEngineService
from app.graph.nodes.understanding_agent import CandidateUnderstandingNode
from app.graph.state import IntelligenceGraphState
from datetime import datetime

def run_test():
    # 1. Create a mock profile simulating an aspiring AI Engineer transitioning from Backend
    mock_data = CompleteOnboardingRequest(
        resume_data=ResumeDataSchema(
            skills=["Python", "FastAPI", "PostgreSQL", "LangChain", "Docker", "Machine Learning"],
            experience=[
                ExperienceSchema(
                    company="Tech Corp",
                    role="Backend Engineer",
                    start_date="2022-01",
                    end_date="2024-01",
                    description="Built scalable backend services using Python and FastAPI. Used PostgreSQL for data storage."
                )
            ],
            projects=[
                ProjectSchema(
                    title="AI Career Assistant",
                    description="An AI tool powered by LangChain.",
                    technologies=["Python", "LangChain", "FastAPI"]
                )
            ],
            certifications=[
                CertificationSchema(name="AWS Certified Developer")
            ],
            education=[],
            summary="A backend engineer passionate about AI."
        ),
        preferences=PreferencesSchema(
            preferred_roles=["AI Engineer", "Machine Learning Engineer"],
            preferred_locations=["Remote"],
            experience_level=ExperienceLevel.fresher
        ),
        resume_metadata=ResumeMetadataSchema(
            file_name="resume.pdf",
            uploaded_at=datetime.utcnow()
        )
    )

    print("--- 1. BUILDING EVIDENCE ---")
    evidence = EvidenceEngineService.build_candidate_evidence(mock_data)
    print("Candidate Level:", evidence.candidate_level.title)
    print("Maturity Signals:", evidence.candidate_maturity)
    print("Inferred Current Domains:", evidence.current_domains)
    print("Inferred Target Domains:", evidence.target_domains)
    print("\n")
    
    print("--- 2. RUNNING UNDERSTANDING AGENT (NODE 1) ---")
    state = IntelligenceGraphState(
        evidence=evidence,
        persona=None,
        persona_generated_at=None,
        market_research=None,
        gap_analysis=None,
        recommendations=None
    )
    
    result = CandidateUnderstandingNode.run(state)
    persona = result["persona"]
    
    print("\n--- 3. GENERATED PERSONA OUTPUT ---")
    print(persona.model_dump_json(indent=2))

if __name__ == "__main__":
    run_test()
