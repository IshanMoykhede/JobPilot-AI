from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver

from app.job_search_agent.state import JobSearchState
from app.job_search_agent.nodes.query_optimizer_node import query_optimizer_node
from app.job_search_agent.nodes.job_retrieval_node import job_retrieval_node
from app.job_search_agent.nodes.job_knowledge_generator_node import job_knowledge_generator_node
from app.job_search_agent.nodes.embedding_node import embedding_store_node
from app.job_search_agent.nodes.semantic_matching_node import semantic_matching_node
from app.job_search_agent.nodes.scorer_node import scorer_node
from app.core.config import settings
from psycopg_pool import ConnectionPool

# 1. Initialize StateGraph
workflow = StateGraph(JobSearchState)

# 2. Add Nodes
workflow.add_node("query_optimizer_node", query_optimizer_node)
workflow.add_node("job_retrieval_node", job_retrieval_node)
workflow.add_node("job_knowledge_generator_node", job_knowledge_generator_node)
workflow.add_node("embedding_store_node", embedding_store_node)
workflow.add_node("semantic_matching_node", semantic_matching_node)
workflow.add_node("scorer_node", scorer_node)

# 3. Define Edges
workflow.add_edge(START, "query_optimizer_node")
workflow.add_edge("query_optimizer_node", "job_retrieval_node")
workflow.add_edge("job_retrieval_node", "job_knowledge_generator_node")
workflow.add_edge("job_knowledge_generator_node", "embedding_store_node")
workflow.add_edge("embedding_store_node", "semantic_matching_node")
workflow.add_edge("semantic_matching_node", "scorer_node")
workflow.add_edge("scorer_node", END)

# 4. Set up Connection Pool for Postgres Checkpointer
# We parse the database URL into the psycopg format if needed, but psycopg can usually handle postgresql:// URIs
# We expose a function to initialize the graph with the checkpointer at runtime
_pool = None
_compiled_app = None

def get_job_search_app():
    """
    Returns the compiled LangGraph application with the PostgresSaver Checkpointer attached.
    Uses a singleton pattern to ensure the graph is only compiled once per server instance.
    """
    global _pool, _compiled_app
    
    if _compiled_app is None:
        print("Initializing Database Pool and Compiling LangGraph...")
        
        # 1. Create a connection pool targeting our PostgreSQL DB only once
        if _pool is None:
            conn_string = settings.DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://")
            _pool = ConnectionPool(conninfo=conn_string, max_size=20, kwargs={"autocommit": True})
        
        # 2. Initialize Checkpointer
        checkpointer = PostgresSaver(_pool)
        
        # 3. Automatically setup checkpoint tables in Postgres if they don't exist
        checkpointer.setup()

        # 4. Compile the graph exactly once
        _compiled_app = workflow.compile(checkpointer=checkpointer)
        
    return _compiled_app
