from sqlalchemy import text
from app.core.database import engine

with engine.begin() as conn:
    result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
    tables = [row[0] for row in result]
    print("Tables:", tables)

    for t in tables:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
        print(f"  {t}: {count} rows")
