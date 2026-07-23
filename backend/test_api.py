import asyncio
from httpx import AsyncClient
from app.core.database import SessionLocal
from app.models.candidate_profile import CandidateProfile  # Import to fix relation
from app.models.user import User

async def test_api():
    # Setup token
    db = SessionLocal()
    user = db.query(User).first()
    db.close()
    
    from jose import jwt
    import os
    from datetime import datetime, timedelta
    
    with open(".env") as f:
        env = dict(line.strip().split("=", 1) for line in f if "=" in line)
        
    secret = env.get("JWT_SECRET_KEY", "supersecretjwtkeyforjobpilotaiportalsigninauthkeys123456")
    algo = env.get("JWT_ALGORITHM", "HS256")
    
    to_encode = {"sub": user.email, "exp": datetime.utcnow() + timedelta(minutes=60)}
    token = jwt.encode(to_encode, secret, algorithm=algo)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with AsyncClient(base_url="http://localhost:8000") as client:
        # Assuming resume_id = a762af22-9e79-431b-9043-2f124e9b058b belongs to this user
        res = await client.get("/api/resume/a762af22-9e79-431b-9043-2f124e9b058b", headers=headers)
        print(f"Status Code: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, dict):
                print(f"Got data with keys: {data.keys()}")
                print(f"Messages count: {len(data.get('messages', []))}")
            else:
                print(f"Got non-dict data: {type(data)}")
        else:
            print(f"Error: {res.text}")

if __name__ == "__main__":
    asyncio.run(test_api())
