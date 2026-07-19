import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

class MatchingContext:
    def __init__(
        self,
        db: Session,
        candidate_knowledge_id: uuid.UUID,
        candidate_knowledge: Dict[str, Any],
        candidate_vector: List[float],
        workspace_id: uuid.UUID,
        conversation_id: Optional[uuid.UUID] = None
    ):
        self.db = db
        self.candidate_knowledge_id = candidate_knowledge_id
        self.candidate_knowledge = candidate_knowledge
        self.candidate_vector = candidate_vector
        self.workspace_id = workspace_id
        self.conversation_id = conversation_id
