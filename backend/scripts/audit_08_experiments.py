import asyncio
import json
import os
from uuid import UUID
from langchain_core.globals import set_debug
set_debug(False)

from app.core.database import SessionLocal
from app.job_search.models.job_search_result import JobSearchResult
from app.job_search.prompts.job_knowledge_prompt import EXTRACTION_PROMPT
from app.job_search.schemas.job_knowledge import BatchJobKnowledgeCreate
from app.conversation.models.conversation import Conversation
from app.models.candidate_profile import CandidateProfile
from app.models.user import User
from app.models.candidate_insights import CandidateInsights

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

async def run_experiments():
    db = SessionLocal()
    job_res = db.query(JobSearchResult).filter(
        JobSearchResult.job_title == 'Data Engineering Internship',
        JobSearchResult.company_name == 'Dataweave Pvt Ltd',
        JobSearchResult.workspace_id == '987e2262-ee5b-4b79-a519-de71604ca153'
    ).first()

    raw_desc = job_res.raw_job_json.get('description', '')
    truncated_desc = raw_desc[:1500] + ('...' if len(raw_desc) > 1500 else '')
    
    company = job_res.company_name if job_res.company_name else "Unknown"
    location = job_res.location if job_res.location else "Unknown"
    
    payload = (
        f"--- JOB INDEX: 0 ---\n"
        f"job_id: {str(job_res.id)}\n"
        f"title: {job_res.job_title}\n"
        f"company: {company}\n"
        f"location: {location}\n"
        f"description: {truncated_desc}\n"
    )
    prompt_original = EXTRACTION_PROMPT.format(batch_size=1, jobs_payload=payload)

    # --- EXPERIMENT 1: Model Comparison ---
    print("\n\n" + "="*50)
    print("EXPERIMENT 1: Model Comparison")
    print("="*50)
    
    gemini_key = getattr(settings, "GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    groq_key = getattr(settings, "GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    
    models = [
        ("gemini-2.0-flash", ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=gemini_key)),
        ("llama-3.3-70b-versatile", ChatGroq(model="llama-3.3-70b-versatile", api_key=groq_key)),
        ("llama-3.1-8b-instant", ChatGroq(model="llama-3.1-8b-instant", api_key=groq_key))
    ]
    
    for name, llm in models:
        print(f"\n--- Testing Model: {name} ---")
        try:
            structured_llm = llm.with_structured_output(BatchJobKnowledgeCreate)
            response = await structured_llm.ainvoke(prompt_original)
            print(json.dumps(response.model_dump(), indent=2))
        except Exception as e:
            print(f"FAILED for {name}: {e}")

    # --- EXPERIMENT 2: Structured Output Isolation ---
    print("\n\n" + "="*50)
    print("EXPERIMENT 2: Structured Output Isolation (llama-3.1-8b-instant)")
    print("="*50)
    llm_8b = ChatGroq(model="llama-3.1-8b-instant", api_key=groq_key)
    print("\n--- Testing Plain Text Generation (No Schema) ---")
    try:
        response_text = await llm_8b.ainvoke(prompt_original)
        print(response_text.content)
    except Exception as e:
        print(f"FAILED: {e}")

    # --- EXPERIMENT 3: Prompt Isolation ---
    print("\n\n" + "="*50)
    print("EXPERIMENT 3: Prompt Isolation (llama-3.1-8b-instant)")
    print("="*50)
    
    isolated_prompt_text = (
        "You are an expert technical recruiter and engineering knowledge analyst.\n"
        "Your task is to analyze a batch of {batch_size} raw job listings and extract a structured, normalized Job Knowledge representation for each.\n\n"
        "Strict Rules:\n"
        "1. Keep the output strictly engineering-domain agnostic. Do not assume Software Engineering if the job is Mechanical, Civil, Electrical, etc.\n"
        "2. For each job, identify the 'primary_domain' and 'secondary_domains'. These MUST be selected from the following valid EngineeringDomain values only:\n"
        "   - 'Software Engineering'\n   - 'Artificial Intelligence / Machine Learning'\n   - 'Data Science'\n   - 'Cyber Security'\n   - 'Cloud Computing'\n   - 'DevOps'\n   - 'Mechanical Engineering'\n   - 'Civil Engineering'\n   - 'Chemical Engineering'\n   - 'Electrical Engineering'\n   - 'Electronics Engineering'\n   - 'Embedded Systems'\n   - 'Unknown Engineering Domain'\n"
        "3. Technologies: Extract explicit tools, programming languages, CAD packages, instruments, or hardware mentioned. Do not hallucinate or infer tools not explicitly in the text.\n"
        "4. Capabilities: Extract normalized technical engineering capabilities (e.g. 'REST API Development', 'CAD Modeling', 'Structural Design', 'PLC Programming', 'Finite Element Analysis', 'PCB Routing').\n"
        "5. Responsibilities: Convert paragraphs into a list of concise, recruiter-style active-verb statements.\n"
        "6. Requirements: Extract certifications, qualifications, mandatory/preferred skills. Do not duplicate technologies.\n"
        "7. Must-have, Preferred, and Bonus Requirements: Categorize the key hiring criteria cleanly.\n"
        "8. Semantic Summary: Generate a 2-3 sentence technical recruiter summary focusing strictly on the engineering work.\n"
        "9. SCHEMA ADHERENCE: You MUST populate the existing structured fields exactly as defined in the provided JSON schema. Ensure nested arrays like 'technologies' and 'capabilities' are fully populated using their respective object schemas (e.g., provide 'name' and 'importance'). Do not invent new fields.\n\n"
        "Batch of Raw Jobs to Process:\n"
        "{jobs_payload}"
    )
    
    prompt_isolated = isolated_prompt_text.format(batch_size=1, jobs_payload=payload)
    
    try:
        structured_llm_8b = llm_8b.with_structured_output(BatchJobKnowledgeCreate)
        response_iso = await structured_llm_8b.ainvoke(prompt_isolated)
        print(json.dumps(response_iso.model_dump(), indent=2))
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(run_experiments())
