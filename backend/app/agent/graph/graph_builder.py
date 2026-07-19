import logging
from langgraph.graph import StateGraph, START, END

from app.agent.schemas.agent_state import AgentState
from app.agent.nodes.intent_router_node import intent_router_node
from app.agent.nodes.job_search_node import job_search_node
from app.agent.nodes.general_chat_node import general_chat_node
from app.agent.nodes.followup_node import followup_node
from app.agent.nodes.resume_tailoring_node import resume_tailoring_node
from app.agent.nodes.interview_node import interview_node
from app.agent.nodes.fallback_node import fallback_node
from app.agent.graph.graph_router import route_intent

logger = logging.getLogger(__name__)

def build_graph():
    """
    Constructs the entire LangGraph orchestration layer.
    Registers nodes, edges, conditional routing, and compiles the graph.
    """
    logger.info("[GraphBuilder] Initializing state graph...")
    workflow = StateGraph(AgentState)

    # Register Nodes
    workflow.add_node("intent_router", intent_router_node)
    workflow.add_node("job_search", job_search_node)
    workflow.add_node("general_chat", general_chat_node)
    workflow.add_node("follow_up", followup_node)
    workflow.add_node("resume_tailoring", resume_tailoring_node)
    workflow.add_node("interview_preparation", interview_node)
    workflow.add_node("fallback", fallback_node)

    # Register Edges
    workflow.add_edge(START, "intent_router")
    
    # Register Conditional Routing
    workflow.add_conditional_edges(
        "intent_router",
        route_intent,
        {
            "job_search": "job_search",
            "general_chat": "general_chat",
            "follow_up": "follow_up",
            "resume_tailoring": "resume_tailoring",
            "interview_preparation": "interview_preparation",
            "fallback": "fallback"
        }
    )

    # End paths
    workflow.add_edge("job_search", END)
    workflow.add_edge("general_chat", END)
    workflow.add_edge("follow_up", END)
    workflow.add_edge("resume_tailoring", END)
    workflow.add_edge("interview_preparation", END)
    workflow.add_edge("fallback", END)

    # Compile the graph
    app_graph = workflow.compile()
    logger.info("[GraphBuilder] Graph compiled successfully.")
    
    return app_graph

# Expose a singleton graph instance
agent_graph = build_graph()
