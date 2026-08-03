import logging
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import get_structured_llm

from app.resume_tailoring_agent_v2.state import ResumeTailoringState
from app.resume_tailoring_agent_v2.schemas.custom import CustomSectionResponse

logger = logging.getLogger(__name__)

CUSTOM_SYSTEM_PROMPT = """You are an expert Resume Tailoring AI. Your task is to generate a custom resume section (e.g., 'Achievements', 'Research', 'Co-curricular Activities') based purely on the user's chat feedback.

You will be provided with:
1. Job Knowledge: The requirements of the target role.
2. Current Draft (optional): The existing custom sections, if any.
3. User Feedback: The user's request to add or modify a custom section (e.g., "Add my Hackathon win to my Achievements").

Your Goal:
Extract the section title the user wants and convert their informal text into 1-3 highly professional, action-oriented bullet points.
Optimize the bullet points so they appeal to the Job Knowledge whenever possible.
DO NOT invent any facts or data that the user did not provide in the User Feedback.

If the user is adding to an existing custom section, append the new bullets to it.
If the user provides vague feedback, output what you can and use the 'question' field to ask for more details.

Respond strictly in the requested JSON format."""

CUSTOM_PROMPT = ChatPromptTemplate.from_messages([
    ("system", CUSTOM_SYSTEM_PROMPT),
    ("user", """
Job Knowledge:
{job_knowledge}

Current Draft (Custom Sections Map):
{current_draft}

User Feedback:
{user_feedback}
""")
])

def custom_section_node(state: ResumeTailoringState) -> ResumeTailoringState:
    """Generates an arbitrary custom section based entirely on user feedback."""
    logger.info("[V2] Executing custom_section_node")
    
    # Extract data from state
    job_knowledge = state.job_knowledge
    
    # Retrieve the history of custom drafts. Custom is a dict mapping section titles to list of strings.
    # e.g., {"Achievements": ["Won hackathon"], "Research": ["Published paper"]}
    custom_history = state.drafts.get("custom", [])
    current_draft = custom_history[-1] if custom_history else "{}"
    
    # Check the user feedback
    latest_msg = state.messages[-1] if state.messages else {}
    user_feedback = latest_msg.get("content", "No specific feedback provided.")
    
    try:
        llm = get_structured_llm(CustomSectionResponse)
        chain = CUSTOM_PROMPT | llm
        
        result: CustomSectionResponse = chain.invoke({
            "job_knowledge": str(job_knowledge),
            "current_draft": str(current_draft),
            "user_feedback": user_feedback
        })
        
        # We need to construct the new dictionary for state.drafts["custom"]
        # It should inherit the previous sections, but overwrite/append the one we just worked on
        import ast
        try:
            current_dict = ast.literal_eval(str(current_draft)) if current_draft != "{}" else {}
        except:
            current_dict = {}
            
        # Update the dictionary with the newly generated section
        current_dict[result.section_title] = [item.model_dump() for item in result.content]
        
        if "custom" not in state.drafts:
            state.drafts["custom"] = []
        state.drafts["custom"].append(current_dict)
        
        reply_parts = [result.explanation, result.question]
        assistant_reply = "\n\n".join(reply_parts)
        
        state.messages.append({
            "role": "assistant",
            "content": assistant_reply
        })
        
        return state
        
    except Exception as e:
        logger.error(f"[V2 Custom Node] Failed to generate custom section: {e}")
        state.messages.append({
            "role": "assistant",
            "content": "I encountered an error while generating the custom section. Please try again."
        })
        return state
