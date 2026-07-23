from typing import Optional, Any
from langgraph.graph import StateGraph, START, END

from app.resume_tailoring_agent.state import ResumeAgentState
from app.resume_tailoring_agent.nodes.intent_router_node import intent_router_node
from app.resume_tailoring_agent.nodes.summary_generator_node import summary_generator_node
from app.resume_tailoring_agent.nodes.project_generator_node import project_generator_node
from app.resume_tailoring_agent.nodes.experience_generator_node import experience_generator_node
from app.resume_tailoring_agent.nodes.skills_generator_node import skills_generator_node
from app.resume_tailoring_agent.nodes.education_generator_node import education_generator_node
from app.resume_tailoring_agent.nodes.certification_generator_node import certification_generator_node
from app.resume_tailoring_agent.nodes.pdf_generation_node import pdf_generation_node
from app.resume_tailoring_agent.nodes.response_node import response_node
from app.resume_tailoring_agent.schemas.messaging import MessageType, MessageSource

def route_from_intent_router(state: ResumeAgentState) -> str:
    if not state.messages:
        return "response_node"
        
    latest_msg = state.messages[-1]
    if latest_msg.message_type == MessageType.WORKFLOW_REQUEST:
        to_node = latest_msg.to_node
        if to_node == MessageSource.SUMMARY_GENERATOR:
            return "summary_generator"
        elif to_node == MessageSource.PROJECT_GENERATOR:
            return "project_generator"
        elif to_node == MessageSource.EXPERIENCE_GENERATOR:
            return "experience_generator"
        elif to_node == MessageSource.SKILLS_GENERATOR:
            return "skills_generator"
        elif to_node == MessageSource.EDUCATION_GENERATOR:
            return "education_generator"
        elif to_node == MessageSource.CERTIFICATION_GENERATOR:
            return "certification_generator"
        elif to_node == MessageSource.PDF_GENERATOR:
            return "pdf_generator"
            
    return "response_node"

from app.core.config import settings
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver

_pool = None
_compiled_app = None

def get_resume_agent_app():
    """
    Returns the compiled LangGraph application with the PostgresSaver Checkpointer attached.
    Uses a singleton pattern to ensure the graph is only compiled once per server instance.
    """
    global _pool, _compiled_app
    
    if _compiled_app is None:
        print("Initializing Database Pool and Compiling Resume Agent LangGraph...")
        
        # 1. Create a connection pool targeting our PostgreSQL DB only once
        if _pool is None:
            conn_string = settings.DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://")
            _pool = ConnectionPool(conninfo=conn_string, max_size=20, kwargs={"autocommit": True})
        
        # 2. Initialize Checkpointer
        checkpointer = PostgresSaver(_pool)
        
        # 3. Automatically setup checkpoint tables in Postgres if they don't exist
        checkpointer.setup()

        workflow = StateGraph(ResumeAgentState)
        
        # Register all nodes
        workflow.add_node("intent_router", intent_router_node)
        workflow.add_node("summary_generator", summary_generator_node)
        workflow.add_node("project_generator", project_generator_node)
        workflow.add_node("experience_generator", experience_generator_node)
        workflow.add_node("skills_generator", skills_generator_node)
        workflow.add_node("education_generator", education_generator_node)
        workflow.add_node("certification_generator", certification_generator_node)
        workflow.add_node("pdf_generator", pdf_generation_node)
        workflow.add_node("response_node", response_node)
        
        # Routing from START
        workflow.add_edge(START, "intent_router")
        
        # Conditional routing from Intent Router to appropriate workflow
        workflow.add_conditional_edges(
            "intent_router",
            route_from_intent_router
        )
        
        # All workflows return control to the Intent Router
        workflow.add_edge("summary_generator", "intent_router")
        workflow.add_edge("project_generator", "intent_router")
        workflow.add_edge("experience_generator", "intent_router")
        workflow.add_edge("skills_generator", "intent_router")
        workflow.add_edge("education_generator", "intent_router")
        workflow.add_edge("certification_generator", "intent_router")
        workflow.add_edge("pdf_generator", "intent_router")
        
        # Response Node sends the final answer out
        workflow.add_edge("response_node", END)
        
        # 4. Compile the graph exactly once
        _compiled_app = workflow.compile(checkpointer=checkpointer)
        
    return _compiled_app
