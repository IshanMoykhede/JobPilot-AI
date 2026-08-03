import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/jobpilot")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    res = conn.execute(text("SELECT job_hash, COUNT(*) FROM job_knowledge GROUP BY job_hash HAVING COUNT(*) > 1"))
    duplicates = res.fetchall()
    print(f"Duplicates in DB: {duplicates}")

    res = conn.execute(text("SELECT id, job_hash, processing_status FROM job_search_result LIMIT 10"))
    results = res.fetchall()
    print("Some JobSearchResults:")
    for r in results:
        print(f"  {r}")
