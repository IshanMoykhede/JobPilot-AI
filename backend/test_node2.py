import sys
import os
import json
import asyncio
from datetime import datetime

# Ensure the app module can be imported
sys.path.append(r"c:\Users\igmoy\OneDrive\Desktop\JobPilot AI\backend")

from app.schemas.candidate_profile import CompleteOnboardingRequest, ResumeDataSchema, ExperienceSchema, ProjectSchema, CertificationSchema, PreferencesSchema, ExperienceLevel, ResumeMetadataSchema
from app.services.evidence_engine import EvidenceEngineService
from app.graph.workflow import build_intelligence_graph
from app.graph.state import IntelligenceGraphState
from app.core.database import SessionLocal

async def run_test():
    # 1. Mock profile: Candidate with 2 years of backend experience desiring to pivot to AI Engineering
    mock_data = CompleteOnboardingRequest(
        resume_data=ResumeDataSchema(
            skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Machine Learning"],
            experience=[
                ExperienceSchema(
                    company="Tech Solutions",
                    role="Backend Engineer",
                    start_date="2022-01",
                    end_date="2024-01",
                    description="Built robust Python microservices and PostgreSQL schemas."
                )
            ],
            projects=[
                ProjectSchema(
                    title="NLP Chatbot",
                    description="Built an NLP RAG chatbot using OpenAI.",
                    technologies=["Python", "OpenAI", "FastAPI"]
                )
            ],
            certifications=[
                CertificationSchema(name="TensorFlow Developer Certificate")
            ],
            education=[],
            summary="A backend engineer aiming to become an AI Engineer."
        ),
        preferences=PreferencesSchema(
            preferred_roles=["AI Engineer", "Backend Engineer"],
            preferred_locations=["Remote"],
            experience_level=ExperienceLevel.two_to_five
        ),
        resume_metadata=ResumeMetadataSchema(
            file_name="resume_ai_engineer.pdf",
            uploaded_at=datetime.utcnow()
        )
    )

    print("--- 1. CALCULATING COMPLETENESS & EVIDENCE ---")
    from app.routes.candidate_profile import calculate_profile_completeness
    percentage, missing = calculate_profile_completeness(mock_data.model_dump(mode="json"))
    print(f"Profile Completeness: {percentage}%")
    print(f"Missing Fields: {missing}")

    evidence = EvidenceEngineService.build_candidate_evidence(mock_data)
    print("Candidate Level:", evidence.candidate_level.title)
    print("Target Roles Inferred:", evidence.target_domains)
    print("\n")
    
    print("--- 2. COMPILING WORKFLOW ---")
    graph = build_intelligence_graph()
    
    print("--- 3. RUNNING INTEGRATED 2-NODE WORKFLOW ASYNC ---")
    state = IntelligenceGraphState(
        evidence=evidence,
        market_intelligence=None,
        market_intelligence_generated_at=None,
        recommendations=None,
        recommendations_generated_at=None
    )
    
    db = SessionLocal()
    config = {"configurable": {"db": db}}
    
    try:
        final_state = await graph.ainvoke(state, config=config)
        
        print("\n--- 4. MARKET INTELLIGENCE OUTPUT ---")
        if final_state.get("market_intelligence"):
            for role, intel in final_state["market_intelligence"].items():
                print(f"\nMarket Expectations for '{role}':")
                print(intel.model_dump_json(indent=2))
            
        print("\n--- 5. AI RECOMMENDATIONS ---")
        if final_state.get("recommendations"):
            for role, rec_res in final_state["recommendations"].items():
                print(f"\nRecommendations for '{role}':")
                print(rec_res.model_dump_json(indent=2))
            
    except Exception as e:
        print("Workflow Execution Failed:", e)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_test())
