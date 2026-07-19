import logging
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.agent.schemas.agent_state import AgentState
from app.agent.graph.graph_builder import agent_graph
from app.agent.nodes.fallback_node import fallback_node
from app.conversation.models.conversation import Conversation
from app.conversation.models.conversation_message import ConversationMessage, Role, MessageType

logger = logging.getLogger(__name__)

class OrchestrationService:
    @staticmethod
    async def run_graph(
        db: Session,
        candidate_profile_id: UUID,
        user_query: str,
        user_id: UUID,
        conversation_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Single backend entry point for all AI interactions.
        Initializes state, persists messages, and invokes the compiled LangGraph.
        """
        logger.info(f"[OrchestrationService] Received query for candidate {candidate_profile_id}")
        
        # 1. Manage Conversation Persistence
        if not conversation_id:
            # Generate a short title from the first query (max 50 chars)
            title = user_query[:50] + ("..." if len(user_query) > 50 else "")
            conversation = Conversation(
                candidate_profile_id=candidate_profile_id,
                title=title
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            conversation_id = conversation.id
            
        # Save User Message
        user_msg = ConversationMessage(
            conversation_id=conversation_id,
            role=Role.USER,
            message_type=MessageType.TEXT,
            content={"text": user_query}
        )
        db.add(user_msg)
        db.commit()
        
        # 2. Initialize AgentState
        initial_state: AgentState = {
            "conversation_id": conversation_id,
            "workspace_id": None,
            "candidate_profile_id": candidate_profile_id,
            "user_query": user_query,
            "intent": None,
            "messages": [],
            "response": None,
            "explanations": None,
            "metadata": {}
        }
        final_state = initial_state  # Default in case graph fails
        
        try:
            logger.info("[OrchestrationService] Invoking LangGraph...")
            final_state = await agent_graph.ainvoke(initial_state)
            
            response = final_state.get("response")
            if not response:
                logger.warning("[OrchestrationService] No response returned from graph, defaulting to fallback.")
                fallback_res = await fallback_node(final_state)
                response = fallback_res["response"]
                final_state["response"] = response
                
        except Exception as e:
            logger.error(f"[OrchestrationService] Uncaught graph exception: {e}")
            fallback_res = await fallback_node(initial_state)
            response = fallback_res["response"]
            final_state["response"] = response

        # 3. Save Assistant Message
        has_workspace = final_state.get("workspace_id") is not None
        assistant_msg = ConversationMessage(
            conversation_id=conversation_id,
            role=Role.ASSISTANT,
            message_type=MessageType.JOB_RESULTS if has_workspace else MessageType.TEXT,
            content=response
        )
        db.add(assistant_msg)
        db.commit()
        
        # Inject conversation_id into response so frontend can track it
        if isinstance(response, dict):
            response["conversation_id"] = str(conversation_id)
        
        return final_state
