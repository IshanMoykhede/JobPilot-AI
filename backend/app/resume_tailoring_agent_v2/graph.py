import logging
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.resume_tailoring_agent_v2.state import ResumeTailoringState

# Import Nodes
from app.resume_tailoring_agent_v2.nodes.intent_router_node import intent_router_node
from app.resume_tailoring_agent_v2.nodes.summary_section_node import summary_section_node
from app.resume_tailoring_agent_v2.nodes.project_section_node import project_section_node
from app.resume_tailoring_agent_v2.nodes.skills_section_node import skills_section_node
from app.resume_tailoring_agent_v2.nodes.experience_section_node import experience_section_node
from app.resume_tailoring_agent_v2.nodes.education_section_node import education_section_node
from app.resume_tailoring_agent_v2.nodes.certification_section_node import certification_section_node
from app.resume_tailoring_agent_v2.nodes.custom_section_node import custom_section_node
from app.resume_tailoring_agent_v2.nodes.general_chat_node import general_chat_node

logger = logging.getLogger(__name__)

def route_intent(state: ResumeTailoringState) -> str:
    """Routes the state to the appropriate section node based on the router's classification."""
    active = state.active_section
    
    if active == "summary":
        return "summary"
    elif active == "projects":
        return "projects"
    elif active == "skills":
        return "skills"
    elif active == "experience":
        return "experience"
    elif active == "education":
        return "education"
    elif active == "certifications":
        return "certifications"
    elif active and active.startswith("custom:"):
        return "custom"
    elif active == "general":
        return "general_chat"
    else:
        # If intent is anything unknown, we end the graph for now.
        return "end"

def build_graph(checkpointer=None):
    """
    Builds and compiles the Resume Tailoring Agent V2 StateGraph.
    Args:
        checkpointer: A LangGraph checkpointer (e.g., MemorySaver or PostgresSaver). 
                      If None, the graph runs without state memory across threads.
    """
    logger.info("[V2 Orchestrator] Building LangGraph Orchestrator")
    
    workflow = StateGraph(ResumeTailoringState)
    
    # 1. Add all nodes
    workflow.add_node("intent_router", intent_router_node)
    
    workflow.add_node("summary", summary_section_node)
    workflow.add_node("projects", project_section_node)
    workflow.add_node("skills", skills_section_node)
    workflow.add_node("experience", experience_section_node)
    workflow.add_node("education", education_section_node)
    workflow.add_node("certifications", certification_section_node)
    workflow.add_node("custom", custom_section_node)
    workflow.add_node("general_chat", general_chat_node)
    
    # 2. Set Entry Point
    workflow.set_entry_point("intent_router")
    
    # 3. Add Conditional Routing from the Intent Router
    workflow.add_conditional_edges(
        "intent_router",
        route_intent,
        {
            "summary": "summary",
            "projects": "projects",
            "skills": "skills",
            "experience": "experience",
            "education": "education",
            "certifications": "certifications",
            "custom": "custom",
            "general_chat": "general_chat",
            "end": END
        }
    )
    
    # 4. All nodes route to END after generating their outputs
    workflow.add_edge("summary", END)
    workflow.add_edge("projects", END)
    workflow.add_edge("skills", END)
    workflow.add_edge("experience", END)
    workflow.add_edge("education", END)
    workflow.add_edge("certifications", END)
    workflow.add_edge("custom", END)
    workflow.add_edge("general_chat", END)
    
    # 5. Compile with the provided checkpointer
    app = workflow.compile(checkpointer=checkpointer)
    return app

# Expose a singleton instance of the compiled graph
resume_tailoring_app = build_graph()
