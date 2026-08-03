import asyncio
import json
import os
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
from app.core.config import settings

async def run_test():
    db = SessionLocal()
    job_res = db.query(JobSearchResult).filter(
        JobSearchResult.job_title == 'Data Engineering Internship',
        JobSearchResult.company_name == 'Dataweave Pvt Ltd'
    ).first()

    if not job_res:
        print("Job not found!")
        return

    raw_desc = job_res.raw_job_json.get('description', '') if job_res.raw_job_json else ''
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
    
    print("\n" + "="*50)
    print("1. RAW SERP PAYLOAD (Input to Prompt)")
    print("="*50)
    print(payload)

    prompt_formatted = EXTRACTION_PROMPT.format(batch_size=1, jobs_payload=payload)
    
    print("\n" + "="*50)
    print("2. FINAL PROMPT AFTER FORMATTING")
    print("="*50)
    print(prompt_formatted)

    groq_key = getattr(settings, "GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    llm = ChatGroq(model="llama-3.1-8b-instant", api_key=groq_key)

    print("\n" + "="*50)
    print("3. RAW LLM RESPONSE (Plain Text JSON, No Pydantic Parsing)")
    print("="*50)
    try:
        # Just ask the model directly for JSON without Pydantic schema enforcing
        prompt_with_json_instruction = prompt_formatted + "\nReturn ONLY valid JSON. No markdown formatting or explanation."
        raw_response = await llm.ainvoke(prompt_with_json_instruction)
        print(raw_response.content)
    except Exception as e:
        print(f"Failed to get raw text: {e}")

    print("\n" + "="*50)
    print("4. PARSED PYDANTIC OBJECT (Langchain with_structured_output)")
    print("="*50)
    try:
        structured_llm = llm.with_structured_output(BatchJobKnowledgeCreate)
        response = await structured_llm.ainvoke(prompt_formatted)
        print(json.dumps(response.model_dump(), indent=2))
        
        job_data = response.jobs[0]
        print("\n" + "="*50)
        print("5. VALIDATION RESULT")
        print("="*50)
        print(f"Technologies length: {len(job_data.technologies)}")
        print(f"Technologies type: {type(job_data.technologies[0]) if job_data.technologies else 'Empty'}")
        print(f"Technologies: {job_data.technologies}")
        
        print(f"\nCapabilities length: {len(job_data.capabilities)}")
        print(f"Capabilities type: {type(job_data.capabilities[0]) if job_data.capabilities else 'Empty'}")
        print(f"Capabilities: {job_data.capabilities}")
        
        print(f"\nResponsibilities length: {len(job_data.responsibilities)}")
        print(f"Responsibilities type: {type(job_data.responsibilities[0]) if job_data.responsibilities else 'Empty'}")
        print(f"Responsibilities: {job_data.responsibilities}")
        
    except Exception as e:
        print(f"Pydantic extraction failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
