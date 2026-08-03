import asyncio
from app.job_search.models.job_knowledge import JobKnowledge
from app.schemas.evidence import EngineeringDomain
from app.job_search_agent.matching.services.deterministic_matcher import DeterministicMatcher
from app.job_search_agent.matching.core import matching_config
from app.conversation.models.conversation import Conversation
from app.models.candidate_profile import CandidateProfile
from app.models.user import User
from app.models.candidate_insights import CandidateInsights

def run_test():
    # Mock Candidate
    candidate = {
        "candidate_identity": {
            "engineering_domains": ["Data Science"],
            "primary_technology_stack": ["React", "Node.js", "MongoDB"],
            "supporting_technologies": [],
            "strongest_capabilities": ["coding", "problem solving", "api development"],
        },
        "candidate_level": {
            "total_months_experience": 36
        }
    }

    # Mock Job
    job = JobKnowledge(
        job_title="Data Engineering Internship",
        company_name="Dataweave Pvt Ltd",
        location="Bengaluru, Karnataka, India",
        primary_domain=EngineeringDomain.DATA_SCIENCE,
        secondary_domains=[],
        technologies=["React", "Python", "Docker"],
        capabilities=["coding", "scraping", "problem solving"],
        semantic_summary="Mid level data engineering intern."
    )

    print("--- TECHNOLOGIES ---")
    print(f"Candidate Technologies: {candidate['candidate_identity']['primary_technology_stack']}")
    print(f"Job Technologies:       {job.technologies}")
    score, tech_ev = DeterministicMatcher.compare_technologies(candidate, job)
    from app.job_search_agent.matching.schemas.comparison import MatchType
    match = [item.job for item in tech_ev if item.match_type in (MatchType.EXACT, MatchType.CANONICAL, MatchType.PARTIAL)]
    miss = [item.job for item in tech_ev if item.match_type == MatchType.MISSING]
    print(f"Intersection (Matching): {match}")
    print(f"Missing:                 {miss}")
    print(f"Technology Score:        {score:.2f} / {matching_config.TECH_WEIGHT}")

    print("\n--- CAPABILITIES ---")
    print(f"Candidate Capabilities: {candidate['candidate_identity']['strongest_capabilities']}")
    print(f"Job Capabilities:       {job.capabilities}")
    score, cap_ev = DeterministicMatcher.compare_capabilities(candidate, job)
    match = [item.job for item in cap_ev if item.match_type in (MatchType.EXACT, MatchType.CANONICAL, MatchType.PARTIAL)]
    miss = [item.job for item in cap_ev if item.match_type == MatchType.MISSING]
    print(f"Intersection (Matching): {match}")
    print(f"Missing:                 {miss}")
    print(f"Capability Score:        {score:.2f} / {matching_config.CAPABILITY_WEIGHT}")

    print("\n--- FULL SCORE BREAKDOWN ---")
    score, match, miss = DeterministicMatcher.calculate_score(candidate, job)
    print(f"Total Score:     {score:.2f} / 100")
    print(f"All Matching:    {match}")
    print(f"All Missing:     {miss}")

if __name__ == "__main__":
    run_test()
