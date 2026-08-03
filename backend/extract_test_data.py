import os
import sys
import json
import asyncio
from sqlalchemy.future import select

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import async_session_maker
from app.models.job_document import JobDocument
from app.models.candidate_insights import CandidateInsights

async def extract_data():
    async with async_session_maker() as session:
        # Get one Job Document (job knowledge)
        stmt_job = select(JobDocument).limit(1)
        result_job = await session.execute(stmt_job)
        job_doc = result_job.scalar_one_or_none()
        
        if job_doc:
            job_data = job_doc.extracted_json
            with open("test_job_knowledge.json", "w", encoding="utf-8") as f:
                json.dump(job_data, f, indent=2)
            print("Extracted test_job_knowledge.json")
        else:
            print("No JobDocument found.")
            
        # Get one Candidate Insight
        stmt_cand = select(CandidateInsights).limit(1)
        result_cand = await session.execute(stmt_cand)
        cand_doc = result_cand.scalar_one_or_none()
        
        if cand_doc:
            cand_data = cand_doc.artifact_json
            with open("test_candidate_insights.json", "w", encoding="utf-8") as f:
                json.dump(cand_data, f, indent=2)
            print("Extracted test_candidate_insights.json")
        else:
            print("No CandidateInsights found.")

if __name__ == "__main__":
    asyncio.run(extract_data())
