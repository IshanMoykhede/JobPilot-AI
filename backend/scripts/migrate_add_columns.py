"""
Migration script: Add new columns to job_search_results table.

Adds: work_mode, deterministic_score, final_score, matching_skills, missing_skills

Also renames final_match_score -> final_score if it exists.
"""
from app.core.database import engine
from sqlalchemy import text, inspect

def run_migration():
    inspector = inspect(engine)
    existing_columns = [col["name"] for col in inspector.get_columns("job_search_results")]
    
    migrations = []
    
    if "work_mode" not in existing_columns:
        migrations.append("ALTER TABLE job_search_results ADD COLUMN work_mode VARCHAR NULL")
    
    if "deterministic_score" not in existing_columns:
        migrations.append("ALTER TABLE job_search_results ADD COLUMN deterministic_score FLOAT NULL")
    
    if "final_score" not in existing_columns:
        if "final_match_score" in existing_columns:
            migrations.append("ALTER TABLE job_search_results RENAME COLUMN final_match_score TO final_score")
        else:
            migrations.append("ALTER TABLE job_search_results ADD COLUMN final_score FLOAT NULL")
    
    if "matching_skills" not in existing_columns:
        migrations.append("ALTER TABLE job_search_results ADD COLUMN matching_skills JSON NULL")
    
    if "missing_skills" not in existing_columns:
        migrations.append("ALTER TABLE job_search_results ADD COLUMN missing_skills JSON NULL")

    if "comparison_evidence" not in existing_columns:
        migrations.append("ALTER TABLE job_search_results ADD COLUMN comparison_evidence JSONB NULL")

    if "ai_explanation" not in existing_columns:
        migrations.append("ALTER TABLE job_search_results ADD COLUMN ai_explanation JSON NULL")

    if not migrations:
        print("[Migration] All columns already exist. Nothing to do.")
        return

    with engine.connect() as conn:
        for sql in migrations:
            print(f"[Migration] Running: {sql}")
            conn.execute(text(sql))
        conn.commit()
    
    print(f"[Migration] Successfully applied {len(migrations)} migration(s).")

if __name__ == "__main__":
    run_migration()
