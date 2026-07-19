import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.conversation.models.conversation_message import ConversationMessage, Role, MessageType

logger = logging.getLogger(__name__)

class ConversationHistoryService:
    @staticmethod
    def add_message(
        db: Session,
        conversation_id: UUID,
        role: str,
        content: Any,
        message_type: str = "TEXT",
        message_metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationMessage:
        """
        Add a message to a conversation.
        """
        logger.info(f"[ConversationHistory] Adding message role={role} type={message_type} to conv={conversation_id}")
        role_enum = Role[role] if role in Role.__members__ else Role.USER
        msg_type_enum = MessageType[message_type] if message_type in MessageType.__members__ else MessageType.TEXT
        
        message = ConversationMessage(
            conversation_id=conversation_id,
            role=role_enum,
            message_type=msg_type_enum,
            content=content,
            message_metadata=message_metadata
        )
        db.add(message)
        db.flush()
        return message

    @staticmethod
    def load_messages(db: Session, conversation_id: UUID) -> List[ConversationMessage]:
        """
        Load all messages in a conversation, sorted by time.
        """
        return db.query(ConversationMessage).filter(ConversationMessage.conversation_id == conversation_id).order_by(ConversationMessage.created_at.asc()).all()

    @staticmethod
    def append_user_message(db: Session, conversation_id: UUID, content: Any, metadata: Optional[Dict[str, Any]] = None) -> ConversationMessage:
        """
        Append a USER message.
        """
        return ConversationHistoryService.add_message(
            db=db,
            conversation_id=conversation_id,
            role="USER",
            content=content,
            message_type="TEXT",
            message_metadata=metadata
        )

    @staticmethod
    def append_assistant_message(db: Session, conversation_id: UUID, content: Any, message_type: str = "TEXT", metadata: Optional[Dict[str, Any]] = None) -> ConversationMessage:
        """
        Append an ASSISTANT message.
        """
        return ConversationHistoryService.add_message(
            db=db,
            conversation_id=conversation_id,
            role="ASSISTANT",
            content=content,
            message_type=message_type,
            message_metadata=metadata
        )

    @staticmethod
    def append_system_message(db: Session, conversation_id: UUID, content: Any, metadata: Optional[Dict[str, Any]] = None) -> ConversationMessage:
        """
        Append a SYSTEM message.
        """
        return ConversationHistoryService.add_message(
            db=db,
            conversation_id=conversation_id,
            role="SYSTEM",
            content=content,
            message_type="SYSTEM_EVENT",
            message_metadata=metadata
        )

    @staticmethod
    def append_tool_message(db: Session, conversation_id: UUID, content: Any, metadata: Optional[Dict[str, Any]] = None) -> ConversationMessage:
        """
        Append a TOOL message.
        """
        return ConversationHistoryService.add_message(
            db=db,
            conversation_id=conversation_id,
            role="TOOL",
            content=content,
            message_type="TOOL_RESULT",
            message_metadata=metadata
        )
