import logging
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import get_structured_llm

from app.resume_tailoring_agent_v2.state import ResumeTailoringState
from app.resume_tailoring_agent_v2.schemas.education import EducationSectionResponse

logger = logging.getLogger(__name__)

EDUCATION_SYSTEM_PROMPT = """You are an expert Resume Tailoring AI. Your task is to generate or revise the 'Education' section of a resume.

You will be provided with:
1. Job Knowledge: The requirements of the target role.
2. Education Intelligence: The candidate's raw academic history.
3. Current Draft (optional): The existing tailored draft, if we are revising.
4. User Feedback (optional): Specific requests from the user to change the draft.

Your Goal:
Output a clean, professional education section. Highlight relevant coursework or honors if they align with the Job Knowledge.

CRITICAL RULES:
1. DO NOT DROP ANY DEGREES. You MUST include every single degree/school listed in the Education Intelligence. Never trim or summarize the candidate's academic history.
2. If the candidate has absolutely NO education listed, return an empty array for 'content' and kindly inform the user via the 'explanation' field. Do NOT invent degrees.
3. If the job strictly requires a specific degree (e.g., Masters) and the candidate doesn't have it, populate the 'gap_warning' to alert them.
4. If User Feedback is provided, you MUST apply their requested changes to the Current Draft.

Respond strictly in the requested JSON format."""

EDUCATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", EDUCATION_SYSTEM_PROMPT),
    ("user", """
Job Knowledge:
{job_knowledge}

Education Intelligence:
{education_intelligence}

Current Draft:
{current_draft}

User Feedback:
{user_feedback}
""")
])

def education_section_node(state: ResumeTailoringState) -> ResumeTailoringState:
    """Generates or revises the Education section."""
    logger.info("[V2] Executing education_section_node")
    
    job_knowledge = state.job_knowledge
    education_intelligence = state.user_knowledge.get("education_intelligence", [])
    
    edu_history = state.drafts.get("education", [])
    current_draft = edu_history[-1] if edu_history else "No current draft exists."
    
    latest_msg = state.messages[-1] if state.messages else {}
    user_feedback = latest_msg.get("content", "No specific feedback provided.")
    
    try:
        llm = get_structured_llm(EducationSectionResponse)
        chain = EDUCATION_PROMPT | llm
        
        result: EducationSectionResponse = chain.invoke({
            "job_knowledge": str(job_knowledge),
            "education_intelligence": str(education_intelligence),
            "current_draft": str(current_draft),
            "user_feedback": user_feedback
        })
        
        new_draft = [item.model_dump() for item in result.content]
        if "education" not in state.drafts:
            state.drafts["education"] = []
        state.drafts["education"].append(new_draft)
        
        reply_parts = [result.explanation]
        if result.gap_warning:
            reply_parts.append(f"⚠️ Note: {result.gap_warning}")
        reply_parts.append(result.question)
        
        assistant_reply = "\n\n".join(reply_parts)
        
        state.messages.append({
            "role": "assistant",
            "content": assistant_reply
        })
        
        return state
        
    except Exception as e:
        logger.error(f"[V2 Education Node] Failed to generate education: {e}")
        state.messages.append({
            "role": "assistant",
            "content": "I encountered an error while generating the education section. Please try again."
        })
        return state
