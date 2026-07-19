import asyncio
import os
import sys

# Ensure backend path is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.job_search.models.search_workspace import SearchWorkspace
from app.job_search.models.job_search_result import JobSearchResult

def export_jobs(email: str):
    db = SessionLocal()
    try:
        # Find user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User with email {email} not found.")
            return
            
        # Find profile
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
        if not profile:
            print(f"Candidate profile for user {email} not found.")
            return

        # Get the most recent workspace for this profile
        latest_workspace = db.query(SearchWorkspace).filter(
            SearchWorkspace.candidate_profile_id == profile.id
        ).order_by(SearchWorkspace.created_at.desc()).first()
        if not latest_workspace:
            print("No workspaces found.")
            return

        print(f"Latest Workspace ID: {latest_workspace.id}")
        print(f"Original Query: {latest_workspace.original_query}")

        # Get the jobs for this workspace
        jobs = db.query(JobSearchResult).filter(JobSearchResult.workspace_id == latest_workspace.id).order_by(JobSearchResult.final_score.desc()).all()
        
        output_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "jobs.txt")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"Query: {latest_workspace.original_query}\n")
            f.write(f"Total Jobs Found: {len(jobs)}\n")
            f.write("="*50 + "\n\n")
            
            for idx, job in enumerate(jobs, 1):
                f.write(f"Job #{idx}\n")
                f.write(f"Title: {job.job_title}\n")
                f.write(f"Company: {job.company_name or 'N/A'}\n")
                f.write(f"Location: {job.location or 'N/A'}\n")
                f.write(f"Match Score: {job.final_score}\n")
                
                raw = job.raw_job_json or {}
                link = raw.get("link", "N/A")
                f.write(f"Link: {link}\n")
                
                desc = raw.get("description", "N/A")
                f.write(f"\nDescription Snippet:\n{desc[:500]}...\n")
                f.write("-" * 50 + "\n\n")
                
        print(f"Successfully exported {len(jobs)} jobs to {output_path}")

    except Exception as e:
        print(f"Error exporting jobs: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    export_jobs("moykhedeishan@gmail.com")
