from langgraph.graph import StateGraph, START, END
from app.ai_job_search_agent.state import V2AgentState

def build_graph():
    """
    Builds the Job Search Agent V2 state graph.
    """
    builder = StateGraph(V2AgentState)
    
    # Placeholder: currently an empty graph connecting START to END
    builder.add_edge(START, END)
    
    return builder.compile()

# Compile the empty graph for import elsewhere
graph = build_graph()
