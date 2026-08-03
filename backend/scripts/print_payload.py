import json
from uuid import UUID
from app.core.database import SessionLocal
from app.job_search_agent.presentation.job_search_presentation_builder import JobSearchPresentationBuilder
from app.job_search_agent.explanation.schemas.explanation import JobExplanation
from app.conversation.models.conversation import Conversation
from app.models.candidate_profile import CandidateProfile
from app.models.user import User
from app.job_search.models.job_search_result import JobSearchResult
from app.models.candidate_insights import CandidateInsights
from sqlalchemy.orm import Session

def print_workspace_results():
    db = SessionLocal()
    try:
        job_results = db.query(JobSearchResult).filter(
            JobSearchResult.job_title == 'Data Engineering Internship'
        ).all()
        for job_res in job_results:
            print(f'Job ID: {job_res.id}')
            print(f'Workspace ID: {job_res.workspace_id}')
            print(f'Job Knowledge ID: {job_res.job_knowledge_id}')
            if job_res.job_knowledge:
                print('--- JobKnowledge ---')
                print(json.dumps(job_res.job_knowledge.__dict__, default=str, indent=2))


        # Candidate Knowledge
        insight = db.query(CandidateInsights).filter(
            CandidateInsights.candidate_profile_id == '78841063-f785-46da-af24-bbeb1976d801',
            CandidateInsights.artifact_type == 'CANDIDATE_KNOWLEDGE'
        ).order_by(CandidateInsights.created_at.desc()).first()
        print('\n--- CandidateKnowledge ---')
        print(json.dumps(insight.artifact_json, default=str, indent=2))
        
    finally:
        db.close()

if __name__ == "__main__":
    print_workspace_results()
