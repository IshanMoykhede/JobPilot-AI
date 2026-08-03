import asyncio
import json
import os
import sys

# Ensure we can import from the app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app.job_search.providers.serp_provider import SerpJobProvider
from app.job_search.services.serp_service import RawJobParser

async def test_serp_api():
    # Bypassing Gemini to avoid rate limits
    query = "software engineering jobs for freshers in Pune"
    print(f"Direct Query to SerpAPI: {query}")
    
    # Call Serp API directly without fallback
    print("\nCalling SerpAPI directly...")
    provider = SerpJobProvider()
    raw_results = provider.fetch_jobs(query)
    
    print(f"Number of jobs fetched: {len(raw_results)}")
    
    # Parse jobs to get clean dicts
    print("\nParsing Results...")
    parsed_jobs = [RawJobParser.parse_raw_job(job).model_dump() for job in raw_results]
    
    # Write to file
    output_file = "serp_test_results.json"
    with open(output_file, "w") as f:
        json.dump({
            "original_query": query,
            "total_jobs_returned": len(parsed_jobs),
            "jobs": parsed_jobs
        }, f, indent=4)
        
    print(f"\nSuccess! Full results saved to: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    asyncio.run(test_serp_api())
