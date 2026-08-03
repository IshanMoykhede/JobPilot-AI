import asyncio
from app.job_search.models.job_knowledge import JobKnowledge
from app.schemas.evidence import EngineeringDomain
from app.embedding.services.job_document_builder import JobDocumentBuilder
from app.conversation.models.conversation import Conversation
from app.models.candidate_profile import CandidateProfile
from app.models.user import User
from app.models.candidate_insights import CandidateInsights

def run_test():
    # Mocking the extracted JobKnowledge from Phase 4
    jk = JobKnowledge(
        job_title="Data Engineering Internship",
        company_name="Dataweave Pvt Ltd",
        location="Bengaluru, Karnataka, India",
        employment_type="",
        experience_level="",
        primary_domain=EngineeringDomain.DATA_SCIENCE,
        secondary_domains=[],
        technologies=[],
        capabilities=["coding", "scraping", "problem solving"],
        responsibilities=[],
        must_have_requirements=[],
        preferred_requirements=[],
        semantic_summary="Develop data engineering skills through a paid internship."
    )
    
    doc = JobDocumentBuilder.build_document(jk)
    print(doc)

if __name__ == "__main__":
    run_test()
