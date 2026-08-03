import asyncio
from sqlalchemy import text
from app.core.database import engine, Base
from app.job_search.models.job_knowledge import JobKnowledge
import app.job_search.models.job_search_result

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS job_knowledge CASCADE"))
    conn.commit()

print("Dropped job_knowledge.")
Base.metadata.create_all(bind=engine)
print("Recreated job_knowledge.")
