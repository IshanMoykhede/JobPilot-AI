import logging
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import get_structured_llm

from app.resume_tailoring_agent_v2.state import ResumeTailoringState
from app.resume_tailoring_agent_v2.schemas.experience import ExperienceSectionResponse

logger = logging.getLogger(__name__)

EXPERIENCE_SYSTEM_PROMPT = """You are an expert Resume Tailoring AI. Your task is to generate or revise the 'Experience' section of a resume.

You will be provided with:
1. Job Knowledge: The requirements of the target role.
2. Experience Intelligence: The candidate's raw experience history, which consists primarily of Internships and early-career roles.
3. Current Draft (optional): The existing tailored draft, if we are revising.
4. User Feedback (optional): Specific requests from the user to change the draft.

Your Goal:
Output a highly tailored experience section. Since this candidate's experience is heavily based on internships, focus on extracting their learnings, capabilities, and the technologies they were exposed to, framing them as impactful bullet points that align with the Job Knowledge.

CRITICAL RULES AND ATS-OPTIMIZATION:
1. If the candidate has absolutely NO experience, return an empty array for 'content' and use the 'explanation' and 'gap_warning' fields to kindly inform the user. Do NOT invent experience.
2. If their experience is completely unrelated to the job (e.g., Retail, Food Service), focus heavily on transferable soft skills (communication, leadership, time management) rather than forcing technical jargon.
3. Start EVERY bullet point with a strong, impactful action verb (e.g., "Spearheaded", "Engineered", "Facilitated").
4. Focus strictly on the required capabilities and technologies mentioned in the Job Knowledge. Ensure these keywords appear naturally in the bullets.
5. Be metric-driven: Quantify achievements, scale, or scope whenever possible.
6. Keep bullets concise and high-impact. Do not include filler words.
7. If User Feedback is provided, you MUST apply their requested changes to the Current Draft.

Respond strictly in the requested JSON format."""

EXPERIENCE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", EXPERIENCE_SYSTEM_PROMPT),
    ("user", """
Job Knowledge:
{job_knowledge}

Experience Intelligence:
{experience_intelligence}

Current Draft:
{current_draft}

User Feedback:
{user_feedback}
""")
])

def experience_section_node(state: ResumeTailoringState) -> ResumeTailoringState:
    """Generates or revises the Experience section with a focus on Internships."""
    logger.info("[V2] Executing experience_section_node")
    
    # Extract data from state
    job_knowledge = state.job_knowledge
    experience_intelligence = state.user_knowledge.get("experience_intelligence", [])
    
    # Retrieve the history of experience drafts
    exp_history = state.drafts.get("experience", [])
    current_draft = exp_history[-1] if exp_history else "No current draft exists."
    
    # Check if we are revising based on the latest message intent
    latest_msg = state.messages[-1] if state.messages else {}
    user_feedback = latest_msg.get("content", "No specific feedback provided. Generate the best initial draft.")
    
    try:
        llm = get_structured_llm(ExperienceSectionResponse)
        chain = EXPERIENCE_PROMPT | llm
        
        result: ExperienceSectionResponse = chain.invoke({
            "job_knowledge": str(job_knowledge),
            "experience_intelligence": str(experience_intelligence),
            "current_draft": str(current_draft),
            "user_feedback": user_feedback
        })
        
        # 1. Append the new structured draft content to the section's version history
        new_draft = [item.model_dump() for item in result.content]
        if "experience" not in state.drafts:
            state.drafts["experience"] = []
        state.drafts["experience"].append(new_draft)
        
        # 2. Construct the conversational assistant reply
        reply_parts = [result.explanation]
        if result.gap_warning:
            reply_parts.append(f"⚠️ Note: {result.gap_warning}")
        reply_parts.append(result.question)
        
        assistant_reply = "\n\n".join(reply_parts)
        
        # 3. Append to conversation history
        state.messages.append({
            "role": "assistant",
            "content": assistant_reply
        })
        
        return state
        
    except Exception as e:
        logger.error(f"[V2 Experience Node] Failed to generate experience: {e}")
        state.messages.append({
            "role": "assistant",
            "content": "I encountered an error while generating the experience section. Please try again."
        })
        return state
