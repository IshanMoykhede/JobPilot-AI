import logging
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import get_structured_llm

from app.resume_tailoring_agent_v2.state import ResumeTailoringState
from app.resume_tailoring_agent_v2.schemas.certification import CertificationSectionResponse

logger = logging.getLogger(__name__)

CERTIFICATION_SYSTEM_PROMPT = """You are an expert Resume Tailoring AI. Your task is to generate or revise the 'Certifications' section of a resume.

You will be provided with:
1. Job Knowledge: The requirements of the target role.
2. Certification Intelligence: The candidate's raw certifications and associated capabilities.
3. Current Draft (optional): The existing tailored draft, if we are revising.
4. User Feedback (optional): Specific requests from the user to change the draft.

Your Goal:
Output a clean certifications section. Prioritize and highlight certifications that match the capabilities required in the Job Knowledge.

CRITICAL RULES:
1. If the candidate has absolutely NO certifications, return an empty array for 'content'. Use the 'explanation' field to inform the user that this section can be skipped. Do NOT invent certifications.
2. If User Feedback is provided, you MUST apply their requested changes to the Current Draft.

Respond strictly in the requested JSON format."""

CERTIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", CERTIFICATION_SYSTEM_PROMPT),
    ("user", """
Job Knowledge:
{job_knowledge}

Certification Intelligence:
{certification_intelligence}

Current Draft:
{current_draft}

User Feedback:
{user_feedback}
""")
])

def certification_section_node(state: ResumeTailoringState) -> ResumeTailoringState:
    """Generates or revises the Certifications section."""
    logger.info("[V2] Executing certification_section_node")
    
    job_knowledge = state.job_knowledge
    certification_intelligence = state.user_knowledge.get("certification_intelligence", [])
    
    cert_history = state.drafts.get("certifications", [])
    current_draft = cert_history[-1] if cert_history else "No current draft exists."
    
    latest_msg = state.messages[-1] if state.messages else {}
    user_feedback = latest_msg.get("content", "No specific feedback provided.")
    
    try:
        llm = get_structured_llm(CertificationSectionResponse)
        chain = CERTIFICATION_PROMPT | llm
        
        result: CertificationSectionResponse = chain.invoke({
            "job_knowledge": str(job_knowledge),
            "certification_intelligence": str(certification_intelligence),
            "current_draft": str(current_draft),
            "user_feedback": user_feedback
        })
        
        new_draft = [item.model_dump() for item in result.content]
        if "certifications" not in state.drafts:
            state.drafts["certifications"] = []
        state.drafts["certifications"].append(new_draft)
        
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
        logger.error(f"[V2 Certification Node] Failed to generate certifications: {e}")
        state.messages.append({
            "role": "assistant",
            "content": "I encountered an error while generating the certifications section. Please try again."
        })
        return state
