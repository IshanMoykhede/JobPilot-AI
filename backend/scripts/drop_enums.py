from app.core.database import SessionLocal, engine
from sqlalchemy import text

def drop_enums():
    with engine.connect() as connection:
        try:
            connection.execute(text("DROP TYPE IF EXISTS jobknowledgestatus CASCADE;"))
            connection.execute(text("DROP TYPE IF EXISTS jobprocessingstatus CASCADE;"))
            connection.execute(text("DROP TYPE IF EXISTS processingstatus CASCADE;"))
            connection.execute(text("DROP TYPE IF EXISTS searchstatus CASCADE;"))
            connection.commit()
            print("Dropped old enum types successfully.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    drop_enums()
