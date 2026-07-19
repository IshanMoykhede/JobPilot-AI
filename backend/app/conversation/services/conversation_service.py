import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.conversation.models.conversation import Conversation, ConversationType, ConversationStatus

logger = logging.getLogger(__name__)

class ConversationService:
    @staticmethod
    def create_conversation(
        db: Session,
        candidate_profile_id: UUID,
        title: Optional[str] = None,
        conversation_type: str = "GENERAL_CHAT"
    ) -> Conversation:
        """
        Create a new platform conversation.
        """
        logger.info(f"[ConversationService] Creating conversation for profile={candidate_profile_id}")
        conv_type_enum = ConversationType[conversation_type] if conversation_type in ConversationType.__members__ else ConversationType.GENERAL_CHAT
        
        conversation = Conversation(
            candidate_profile_id=candidate_profile_id,
            title=title or "New Search Session",
            conversation_type=conv_type_enum,
            status=ConversationStatus.ACTIVE
        )
        db.add(conversation)
        db.flush()
        return conversation

    @staticmethod
    def load_conversation(db: Session, conversation_id: UUID) -> Optional[Conversation]:
        """
        Load an existing conversation detail.
        """
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()

    @staticmethod
    def rename_conversation(db: Session, conversation_id: UUID, new_title: str) -> Optional[Conversation]:
        """
        Rename an existing conversation.
        """
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.title = new_title
            db.flush()
        return conversation

    @staticmethod
    def archive_conversation(db: Session, conversation_id: UUID) -> Optional[Conversation]:
        """
        Archive a conversation.
        """
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.status = ConversationStatus.ARCHIVED
            db.flush()
        return conversation

    @staticmethod
    def delete_conversation(db: Session, conversation_id: UUID) -> bool:
        """
        Delete a conversation completely.
        """
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            db.delete(conversation)
            db.flush()
            return True
        return False
