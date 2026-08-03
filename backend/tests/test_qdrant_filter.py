import logging
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchAny

load_dotenv()
logging.basicConfig(level=logging.INFO)

url = os.getenv("QDRANT_URL")
api_key = os.getenv("QDRANT_API_KEY")
client = QdrantClient(url=url, api_key=api_key, timeout=10.0)

# 1. Test MatchAny filter
filter_ids = ["1049fff8-ae76-4c93-a47c-0f3dbee81111", "10d4f3b8-8c04-4369-b779-4f22c977de0d"]
res = client.scroll(
    collection_name="job_vectors",
    scroll_filter=Filter(
        must=[
            FieldCondition(key="job_search_result_id", match=MatchAny(any=filter_ids))
        ]
    ),
    limit=5
)
points = res[0]
print(f"MatchAny returned {len(points)} points")

# 2. Test without filter
res = client.scroll(
    collection_name="job_vectors",
    limit=5
)
points = res[0]
print(f"No filter returned {len(points)} points")
