from serpapi import GoogleSearch 
from app.core.config import settings

def extract_job_info(job: dict) -> dict:
    apply_link = ""
    apply_options = job.get("apply_options", [])
    if apply_options and len(apply_options) > 0:
        apply_link = apply_options[0].get("link", "")
    if not apply_link:
        apply_link = job.get("share_link", "")

    return {
        "title": job.get("title", ""),
        "company_name": job.get("company_name", ""),
        "location": job.get("location", ""),
        "description": job.get("description", ""),
        "detected_extensions": job.get("detected_extensions", {}),
        "apply_link": apply_link
    }

def search_jobs_via_serpapi(job_role: str, location: str) -> list[dict]:
    """Fetches up to 30 job listings from SerpApi by paginating through pages."""
    all_jobs = []

    # Base parameters for the first request
    params = {
        "engine": "google_jobs",
        "q": job_role,
        "location": location,
        "hl": "en",
        "gl": "in",  # Set to 'in' for India; change as needed
        "api_key": settings.SERPAPI_API_KEY,
    }

    # --- PAGE 1 ---
    search_page_1 = GoogleSearch(params)
    results_page_1 = search_page_1.get_dict()
    
    # Extract the first batch of jobs (up to 10)
    jobs_page_1 = results_page_1.get("jobs_results", [])
    all_jobs.extend([extract_job_info(job) for job in jobs_page_1])

    # Check if Google returned a token for the next page
    pagination = results_page_1.get("serpapi_pagination", {})
    next_page_token = pagination.get("next_page_token")

    # --- SUBSEQUENT PAGES ---
    while len(all_jobs) < 30 and next_page_token:
        # Add the next_page_token to our parameters to get the next jobs
        params["next_page_token"] = next_page_token

        search_page = GoogleSearch(params)
        results_page = search_page.get_dict()

        jobs_page = results_page.get("jobs_results", [])
        all_jobs.extend([extract_job_info(job) for job in jobs_page])
        
        pagination = results_page.get("serpapi_pagination", {})
        next_page_token = pagination.get("next_page_token")

    return all_jobs[:30]
