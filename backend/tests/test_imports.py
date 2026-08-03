import importlib
import glob
import os

modules = [
    "app.job_search_agent.state",
    "app.job_search_agent.models.job_searches",
    "app.job_search_agent.models.job_knowledge",
    "app.job_search_agent.models.job_match_scores",
    "app.job_search_agent.schemas.job_knowledge",
    "app.job_search_agent.schemas.query_optimizer",
    "app.job_search_agent.utils.token_counter",
    "app.job_search_agent.utils.token_batcher",
    "app.job_search_agent.utils.job_formatter",
    "app.job_search_agent.utils.semantic_formatter",
    "app.job_search_agent.services.serp_api_service",
    "app.job_search_agent.services.embedding_service",
    "app.job_search_agent.services.llm_service",
    "app.job_search_agent.services.qdrant_service",
    "app.job_search_agent.nodes.query_optimizer_node",
    "app.job_search_agent.nodes.job_retrieval_node",
    "app.job_search_agent.nodes.job_knowledge_generator_node",
    "app.job_search_agent.nodes.embedding_node",
    "app.job_search_agent.nodes.semantic_matching_node",
    "app.job_search_agent.nodes.scorer_node",
]

failed = False
for module in modules:
    try:
        importlib.import_module(module)
        print(f"OK: {module}")
    except Exception as e:
        print(f"ERROR in {module}: {type(e).__name__} - {e}")
        failed = True

if failed:
    exit(1)
else:
    print("All modules imported successfully.")
