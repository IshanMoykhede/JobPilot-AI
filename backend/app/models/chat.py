# This module re-exports conversation models from the canonical location
# to maintain backward compatibility with imports.
from app.conversation.models.conversation import Conversation, ConversationType, ConversationStatus
from app.conversation.models.conversation_message import ConversationMessage, Role, MessageType

# Aliases for cleaner imports
Message = ConversationMessage