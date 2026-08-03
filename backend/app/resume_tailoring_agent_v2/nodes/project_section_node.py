import logging
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import get_structured_llm

from app.resume_tailoring_agent_v2.state import ResumeTailoringState
from app.resume_tailoring_agent_v2.schemas.project import ProjectSectionResponse

logger = logging.getLogger(__name__)

PROJECT_SYSTEM_PROMPT = """You are an expert Resume Tailoring AI. Your task is to generate or revise the 'Projects' section of a resume.

You will be provided with:
1. Job Knowledge: The requirements of the target role.
2. Project Intelligence: The candidate's raw project history and context.
3. Current Draft (optional): The existing tailored draft, if we are revising.
4. User Feedback (optional): Specific requests from the user to change the draft.

Your Goal:
Output a highly tailored projects section that highlights the candidate's experience in a way that aligns perfectly with the Job Knowledge.

CRITICAL INSTRUCTIONS FOR ATS-OPTIMIZATION:
1. Start EVERY bullet point with a strong, impactful action verb (e.g., "Architected", "Engineered", "Optimized", "Spearheaded").
2. Focus strictly on the required capabilities and required technologies mentioned in the Job Knowledge. Ensure these keywords appear naturally in the bullets.
3. Be metric-driven: Quantify achievements, performance improvements, or scale whenever possible (e.g., "reduced latency by 40%", "supporting 10k+ concurrent users"). If raw metrics aren't available, focus on the impact and scope of the technical implementation.
4. Keep bullets concise and high-impact. Do not include filler words.

If User Feedback is provided, you MUST apply their requested changes to the Current Draft.

Respond strictly in the requested JSON format."""

PROJECT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", PROJECT_SYSTEM_PROMPT),
    ("user", """
Job Knowledge:
{job_knowledge}

Candidate Project Intelligence:
{project_intelligence}

Current Draft:
{current_draft}

User Feedback:
{user_feedback}
""")
])


def project_section_node(state: ResumeTailoringState) -> ResumeTailoringState:
    """Generates or revises the Projects section based on job knowledge and user feedback."""
    logger.info("[V2] Executing project_section_node")
    
    # Extract data from state
    job_knowledge = state.job_knowledge
    project_intelligence = state.user_knowledge.get("project_intelligence", [])
    
    # Retrieve the history of project drafts. The latest draft is the last item.
    projects_history = state.drafts.get("projects", [])
    current_draft = projects_history[-1] if projects_history else "No current draft exists."
    
    # Check if we are revising based on the latest message intent
    latest_msg = state.messages[-1] if state.messages else {}
    user_feedback = latest_msg.get("content", "No specific feedback provided. Generate the best initial draft.")
    
    try:
        llm = get_structured_llm(ProjectSectionResponse)
        chain = PROJECT_PROMPT | llm
        
        result: ProjectSectionResponse = chain.invoke({
            "job_knowledge": str(job_knowledge),
            "project_intelligence": str(project_intelligence),
            "current_draft": str(current_draft),
            "user_feedback": user_feedback
        })
        
        # 1. Append the new structured draft content to the section's version history
        new_draft = [item.model_dump() for item in result.content]
        if "projects" not in state.drafts:
            state.drafts["projects"] = []
        state.drafts["projects"].append(new_draft)
        
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
        logger.error(f"[V2 Project Node] Failed to generate projects: {e}")
        state.messages.append({
            "role": "assistant",
            "content": "I encountered an error while generating the projects section. Please try again."
        })
        return state
