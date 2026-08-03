import asyncio
from app.job_search.services.serp_service import SerpService
from app.core.config import settings

print(f"SERPAPI KEY: {'SET' if settings.SERPAPI_API_KEY else 'MISSING'}")

def test():
    service = SerpService()
    try:
        jobs = service.search_jobs("backend developer internship opening in pune and mumbai", "maharashtra")
        print(f"Found {len(jobs)} jobs. First job: {jobs[0].get('company_name') if jobs else 'None'}")
    except Exception as e:
        print(f"Exception: {e}")

test()
