import logging
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import get_structured_llm

from app.resume_tailoring_agent_v2.state import ResumeTailoringState
from app.resume_tailoring_agent_v2.schemas.summary import SummarySectionResponse

logger = logging.getLogger(__name__)

SUMMARY_SYSTEM_PROMPT = """You are an expert Resume Tailoring AI. Your task is to generate or revise the 'Professional Summary' section of a resume.

You will be provided with:
1. Job Knowledge: The requirements of the target role.
2. Candidate Identity: The candidate's title and experience level.
3. Core Strengths: The candidate's engineering profile and top skills.
4. Current Draft (optional): The existing tailored draft, if we are revising.
5. User Feedback (optional): Specific requests from the user to change the draft.

Your Goal:
Write a highly impactful, 2-3 sentence professional summary. 
The summary MUST be authentic to the Candidate Identity/Strengths, but it should highlight the specific intersection of their skills with the Job Knowledge.
Do NOT invent years of experience if they are a Fresher. Keep it concise, action-oriented, and ATS-optimized.

If User Feedback is provided, you MUST apply their requested changes to the Current Draft.

Respond strictly in the requested JSON format."""

SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SUMMARY_SYSTEM_PROMPT),
    ("user", """
Job Knowledge:
{job_knowledge}

Candidate Identity & Level:
{candidate_identity}

Core Strengths:
{core_strengths}

Current Draft:
{current_draft}

User Feedback:
{user_feedback}
""")
])

def summary_section_node(state: ResumeTailoringState) -> ResumeTailoringState:
    """Generates or revises the professional summary section."""
    logger.info("[V2] Executing summary_section_node")
    
    # Extract data from state
    job_knowledge = state.job_knowledge
    
    # Combine identity and level
    identity = state.user_knowledge.get("candidate_identity", {})
    level = state.user_knowledge.get("candidate_level", {})
    candidate_identity = f"Title: {identity.get('inferred_title', 'Software Engineer')} | Level: {level.get('title', 'Fresher')}"
    
    # Extract core strengths
    profile = state.user_knowledge.get("engineering_profile", {})
    core_strengths = f"Primary Domains: {', '.join(profile.get('primary_domains', []))} | Strengths: {', '.join(profile.get('core_strengths', []))}"
    
    # Retrieve the history of summary drafts
    summary_history = state.drafts.get("summary", [])
    current_draft = summary_history[-1] if summary_history else "No current draft exists."
    
    # Check if we are revising based on the latest message intent
    latest_msg = state.messages[-1] if state.messages else {}
    user_feedback = latest_msg.get("content", "No specific feedback provided. Generate the best initial draft.")
    
    try:
        llm = get_structured_llm(SummarySectionResponse)
        chain = SUMMARY_PROMPT | llm
        
        result: SummarySectionResponse = chain.invoke({
            "job_knowledge": str(job_knowledge),
            "candidate_identity": candidate_identity,
            "core_strengths": core_strengths,
            "current_draft": str(current_draft),
            "user_feedback": user_feedback
        })
        
        # 1. Append the new draft content (the raw string) to the section's version history
        if "summary" not in state.drafts:
            state.drafts["summary"] = []
        state.drafts["summary"].append([result.content])
        
        # 2. Construct the conversational assistant reply
        reply_parts = [result.explanation, result.question]
        assistant_reply = "\n\n".join(reply_parts)
        
        # 3. Append to conversation history
        state.messages.append({
            "role": "assistant",
            "content": assistant_reply
        })
        
        return state
        
    except Exception as e:
        logger.error(f"[V2 Summary Node] Failed to generate summary: {e}")
        state.messages.append({
            "role": "assistant",
            "content": "I encountered an error while generating the summary section. Please try again."
        })
        return state
