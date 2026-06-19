from langgraph.graph import StateGraph, START, END
from app.graph.state import IntelligenceGraphState
from app.graph.nodes.market_intelligence_agent import MarketIntelligenceNode
from app.graph.nodes.recommendation_agent import RecommendationAgentNode

def build_intelligence_graph():
    """
    Constructs, links, and compiles the Candidate Career Intelligence LangGraph.
    Flow:
    Evidence
       ↓
    Market Intelligence Node (Node 1 - Live Parallel Searches)
       ↓
    AI Recommendation Node (Node 2 - Level-Aware Coach Recommendations)
    """
    workflow = StateGraph(IntelligenceGraphState)
    
    # 1. Add both nodes
    workflow.add_node("market_intelligence", MarketIntelligenceNode.run)
    workflow.add_node("recommendations", RecommendationAgentNode.run)
    
    # 2. Add edges to link them sequentially
    workflow.add_edge(START, "market_intelligence")
    workflow.add_edge("market_intelligence", "recommendations")
    workflow.add_edge("recommendations", END)
    
    # 3. Compile and return the executable graph workflow
    return workflow.compile()
