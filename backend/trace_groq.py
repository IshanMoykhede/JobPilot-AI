import asyncio
import json
from uuid import UUID
from langchain_core.globals import set_debug
set_debug(True)

from app.core.database import SessionLocal
from app.job_search.models.job_search_result import JobSearchResult
from app.job_search.prompts.job_knowledge_prompt import EXTRACTION_PROMPT
from app.core.llm_factory import get_llm
from app.job_search.schemas.job_knowledge import BatchJobKnowledgeCreate
from app.conversation.models.conversation import Conversation
from app.models.candidate_profile import CandidateProfile
from app.models.user import User
from app.models.candidate_insights import CandidateInsights

async def trace_llm():
    db = SessionLocal()
    job_res = db.query(JobSearchResult).filter(
        JobSearchResult.job_title == 'Data Engineering Internship',
        JobSearchResult.company_name == 'Dataweave Pvt Ltd',
        JobSearchResult.workspace_id == '987e2262-ee5b-4b79-a519-de71604ca153'
    ).first()

    raw_desc = job_res.raw_job_json.get('description', '')
    truncated_desc = raw_desc[:1500] + ('...' if len(raw_desc) > 1500 else '')
    
    # Manually resolving the logic
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
    prompt = EXTRACTION_PROMPT.format(batch_size=1, jobs_payload=payload)
    print("\n================ PROMPT ================")
    print(prompt)
    print("========================================\n")

    # We need to call Groq directly since Gemini is rate limited.
    llm = get_llm(model='llama-3.3-70b-versatile')
    structured_llm = llm.with_structured_output(BatchJobKnowledgeCreate)

    print("Calling LLM...")
    response = await structured_llm.ainvoke(prompt)
    print("\n================ PARSED OBJECT ================")
    print(response.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(trace_llm())
