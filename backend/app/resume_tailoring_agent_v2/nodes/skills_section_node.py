import logging
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import get_structured_llm

from app.resume_tailoring_agent_v2.state import ResumeTailoringState
from app.resume_tailoring_agent_v2.schemas.skills import SkillsSectionResponse

logger = logging.getLogger(__name__)

SKILLS_SYSTEM_PROMPT = """You are an expert Resume Tailoring AI. Your task is to generate or revise the 'Skills' section of a resume.

You will be provided with:
1. Job Knowledge: The requirements of the target role.
2. Candidate Skills: A simple list of skills the candidate possesses.
3. Current Draft (optional): The existing tailored draft, if we are revising.
4. User Feedback (optional): Specific requests from the user to change the draft.

Your Goal:
Output a highly tailored skills section. Group the provided Candidate Skills logically (e.g., Languages, Frameworks, Cloud, Tools).
Prioritize skills that match the Job Knowledge. Do not invent skills the candidate does not have.

If User Feedback is provided, you MUST apply their requested changes to the Current Draft.

Respond strictly in the requested JSON format."""

SKILLS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SKILLS_SYSTEM_PROMPT),
    ("user", """
Job Knowledge:
{job_knowledge}

Candidate Skills:
{candidate_skills}

Current Draft:
{current_draft}

User Feedback:
{user_feedback}
""")
])

def skills_section_node(state: ResumeTailoringState) -> ResumeTailoringState:
    """Generates or revises the Skills section based on job knowledge and a simple skill list."""
    logger.info("[V2] Executing skills_section_node")
    
    # Extract data from state
    job_knowledge = state.job_knowledge
    
    # Extract raw unified knowledge
    unified_knowledge = state.user_knowledge.get("unified_knowledge", {})
    
    # Extract just the skill names to save tokens ("no extra shitt")
    raw_skills = []
    if isinstance(unified_knowledge, dict):
        techs = unified_knowledge.get("technologies", [])
        caps = unified_knowledge.get("capabilities", [])
        
        # Safely extract names assuming they are dicts with a "name" key
        raw_skills = [t.get("name") for t in techs if isinstance(t, dict) and t.get("name")] + \
                     [c.get("name") for c in caps if isinstance(c, dict) and c.get("name")]
    
    # Format as a simple comma-separated string
    candidate_skills = ", ".join(raw_skills) if raw_skills else "No explicit skills found."
    
    # Retrieve the history of skills drafts
    skills_history = state.drafts.get("skills", [])
    current_draft = skills_history[-1] if skills_history else "No current draft exists."
    
    # Check if we are revising based on the latest message intent
    latest_msg = state.messages[-1] if state.messages else {}
    user_feedback = latest_msg.get("content", "No specific feedback provided. Generate the best initial draft.")
    
    try:
        llm = get_structured_llm(SkillsSectionResponse)
        chain = SKILLS_PROMPT | llm
        
        result: SkillsSectionResponse = chain.invoke({
            "job_knowledge": str(job_knowledge),
            "candidate_skills": candidate_skills,
            "current_draft": str(current_draft),
            "user_feedback": user_feedback
        })
        
        # 1. Append the new structured draft content to the section's version history
        new_draft = [item.model_dump() for item in result.content]
        if "skills" not in state.drafts:
            state.drafts["skills"] = []
        state.drafts["skills"].append(new_draft)
        
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
        logger.error(f"[V2 Skills Node] Failed to generate skills: {e}")
        state.messages.append({
            "role": "assistant",
            "content": "I encountered an error while generating the skills section. Please try again."
        })
        return state
