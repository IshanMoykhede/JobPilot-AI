from typing import Optional
from pydantic import BaseModel

class OpenSourceContributionEntry(BaseModel):
    project_name: str
    description: str
    repository_url: Optional[str] = None
