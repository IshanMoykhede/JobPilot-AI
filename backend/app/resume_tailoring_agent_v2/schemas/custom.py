from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class CustomItem(BaseModel):
    title: str = Field(description="The title of the item (e.g., '1st Place Winner', 'IEEE Paper', 'GDSC Lead')")
    date: Optional[str] = Field(default=None, description="The date or timeline if provided by the user (e.g., '2023')")
    description: List[str] = Field(description="An array of professional, ATS-optimized bullet points detailing the item.")

class CustomSectionResponse(BaseModel):
    section: Literal["custom"] = Field(description="Must be 'custom'")
    section_title: str = Field(description="The formal title of the section (e.g., 'Achievements', 'Research', 'Co-curricular Activities')")
    content: List[CustomItem] = Field(description="The list of items to add to this custom section.")
    explanation: str = Field(description="A brief explanation of how the custom section was generated.")
    question: str = Field(description="A closing question asking the user if they approve.")
