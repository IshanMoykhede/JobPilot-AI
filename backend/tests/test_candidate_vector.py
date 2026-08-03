import logging
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()
logging.basicConfig(level=logging.INFO)

url = os.getenv("QDRANT_URL")
api_key = os.getenv("QDRANT_API_KEY")
client = QdrantClient(url=url, api_key=api_key, timeout=10.0)

try:
    res = client.scroll(
        collection_name="candidate_vectors",
        limit=1,
        with_vectors=True
    )
    points = res[0]
    for p in points:
        print(f"Point ID: {p.id}")
        print(f"Vector type: {type(p.vector)}, length: {len(p.vector) if p.vector else 'None'}")
        print(f"Payload: {p.payload}")
except Exception as e:
    print(f"Error: {e}")
