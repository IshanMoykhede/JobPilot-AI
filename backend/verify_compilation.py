import os
import sys
from dotenv import load_dotenv

# Load env variables from project root
load_dotenv(os.path.join(os.getcwd(), '.env'))

try:
    from app.core import llm_factory
    from app.services import resume_parser
    from app.services import candidate_synthesizer
    from app.services import academic_intelligence
    from app.services import project_intelligence
    from app.services import experience_intelligence
    from app.services import knowledge_fusion
    from app.agent.nodes import intent_router_node
    from app.graph.nodes import market_intelligence_agent
    from app.graph.nodes import recommendation_agent

    print("SUCCESS: All imports succeeded! Compilation is verified.")
except Exception as e:
    print(f"FAILED: Import/Compilation error: {e}")
    sys.exit(1)
