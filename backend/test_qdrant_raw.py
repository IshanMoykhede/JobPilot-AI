import logging
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()
logging.basicConfig(level=logging.INFO)

try:
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    client = QdrantClient(url=url, api_key=api_key, timeout=10.0)
    col = client.get_collection("job_vectors")
    print(f"Collection status: {col.status}")
    print(f"Points count: {col.points_count}")
    
    res = client.scroll(
        collection_name="job_vectors",
        limit=5
    )
    points = res[0]
    print(f"Scrolled {len(points)} points")
    for p in points:
        print(f" - Point ID: {p.id}")
        print(f"   Payload: {p.payload}")
except Exception as e:
    print(f"Error: {e}")
