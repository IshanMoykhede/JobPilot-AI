from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum

class IntentType(str, Enum):
    NEW_SEARCH = "NEW_SEARCH"
    FOLLOW_UP = "FOLLOW_UP"
    GENERAL = "GENERAL"

class IntentClassification(BaseModel):
    """Output of the Intent Router."""
    intent: IntentType = Field(description="The classified intent of the user's query.")

class SearchExtraction(BaseModel):
    """Output of the Extraction Node."""
    job_role: str = Field(description="The highly optimized job role to search for (e.g., 'Software Engineer').")
    location: Optional[str] = Field(None, description="The location for the job search.")
    additional_requirements: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Flexible dictionary to store arbitrary user preferences like 'remote', 'salary', etc."
    )

class ActivityLog(BaseModel):
    """Log entry for AI agent actions."""
    node_name: str
    input_summary: str
    reasoning: str
    output_summary: str
