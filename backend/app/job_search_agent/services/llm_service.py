from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type

from app.job_search_agent.schemas.job_knowledge import JobKnowledgeBatch
from app.job_search_agent.prompts.job_knowledge_prompt import JOB_KNOWLEDGE_SYSTEM_PROMPT
from app.job_search_agent.prompts.query_optimizer_prompt import QUERY_OPTIMIZER_PROMPT
from app.job_search_agent.schemas.query_optimizer import OptimizedQuery
from app.job_search_agent.utils.job_formatter import format_job_batch
from app.core.config import settings
import groq

# --------------------------------------------------------
# LLM Initialization
# --------------------------------------------------------

llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model="llama-3.1-8b-instant"
)

structured_job_llm = llm.with_structured_output(JobKnowledgeBatch)
structured_query_llm = llm.with_structured_output(OptimizedQuery)

job_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", JOB_KNOWLEDGE_SYSTEM_PROMPT),
        ("user", "{jobs}")
    ]
)

query_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", QUERY_OPTIMIZER_PROMPT),
        ("user", "{query}")
    ]
)

job_chain = job_prompt | structured_job_llm
query_chain = query_prompt | structured_query_llm

# --------------------------------------------------------
# Services
# --------------------------------------------------------

# Retry on RateLimitError, wait 60 seconds, max 3 attempts
@retry(
    retry=retry_if_exception_type(groq.RateLimitError),
    wait=wait_fixed(60),
    stop=stop_after_attempt(3),
    reraise=True
)
def generate_job_knowledge(batch: list[dict]) -> JobKnowledgeBatch:
    """
    Converts a batch of raw jobs into structured JobKnowledge objects.
    Automatically retries on 429 RateLimitError (waits 60s).
    """
    formatted_jobs = format_job_batch(batch)

    response = job_chain.invoke(
        {
            "jobs": formatted_jobs
        }
    )

    return response

@retry(
    retry=retry_if_exception_type(groq.RateLimitError),
    wait=wait_fixed(60),
    stop=stop_after_attempt(3),
    reraise=True
)
def optimize_query(user_query: str) -> OptimizedQuery:
    """
    Extracts the structured job role and location from a raw user string.
    Automatically retries on 429 RateLimitError (waits 60s).
    """
    response = query_chain.invoke(
        {
            "query": user_query
        }
    )

    return response
