from app.core.database import SessionLocal
from app.conversation.models.conversation import Conversation
from app.conversation.models.conversation_message import ConversationMessage
from app.job_search.models.search_workspace import SearchWorkspace
from app.job_search.models.job_search_result import JobSearchResult
from app.job_search.models.job_knowledge import JobKnowledge
import json

db = SessionLocal()
w = db.query(SearchWorkspace).order_by(SearchWorkspace.created_at.desc()).first()
print('Workspace ID:', w.id)
print('Total Jobs Fetched:', w.total_jobs_fetched)
print('Jobs in DB:', len(w.job_results))

c = db.query(Conversation).filter_by(id=w.conversation_id).first()
if c:
    for m in c.messages[-5:]:
        print(f"Role: {m.role}, Type: {m.message_type}")
        print(f"Content: {str(m.content)[:500]}")
