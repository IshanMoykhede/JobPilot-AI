import json
from sqlalchemy import text
from app.core.database import engine

with engine.begin() as conn:
    row = conn.execute(text(
        "SELECT artifact_json, status, generated_at FROM candidate_insights ORDER BY created_at DESC LIMIT 1"
    )).fetchone()

if row:
    output = {
        "status": row[1],
        "generated_at": str(row[2]),
        "candidate_knowledge": row[0]
    }
    with open("candidate_knowledge_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print("Written to candidate_knowledge_output.json")
else:
    print("No insights found in database.")
