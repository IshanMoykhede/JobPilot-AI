from typing_extensions import TypedDict
from typing import Optional, Dict, List
from datetime import datetime
from app.schemas.evidence import CandidateEvidence
from app.graph.schemas.market_intelligence import MarketIntelligence, RecommendationResult

class IntelligenceGraphState(TypedDict):
    """
    This is the "memory" of our LangGraph execution.
    It holds the data that gets passed from node to node.
    """
    # Input from Evidence Engine
    evidence: CandidateEvidence
    
    # Output of Node 1: Market Intelligence (keyed by role name)
    market_intelligence: Optional[Dict[str, MarketIntelligence]]
    market_intelligence_generated_at: Optional[datetime]
    
    # Output of Node 2: AI Recommendations (keyed by role name)
    recommendations: Optional[Dict[str, RecommendationResult]]
    recommendations_generated_at: Optional[datetime]

