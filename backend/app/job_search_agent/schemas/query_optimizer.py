from pydantic import BaseModel, Field

class OptimizedQuery(BaseModel):
    job_role: str = Field(
        description="The standardized job title to search for (e.g., 'Backend Developer Internship')."
    )

    location: str = Field(
        description=(
            "The location formatted strictly as 'City, State, Country' in Title Case "
            "(e.g., 'Pune, Maharashtra, India'). "
            "CRITICAL: If the user only provides a city name in their prompt, you MUST infer "
            "and append the correct state and country automatically."
        )
    )
