import json
import logging
from typing import List
import asyncio

from app.core.llm_factory import get_llm
from langchain_core.prompts import ChatPromptTemplate


from app.core.config import settings
from app.schemas.candidate_profile import ExperienceSchema
from app.schemas.evidence import ExperienceIntelligence
from pydantic import SecretStr
from typing import cast

logger = logging.getLogger(__name__)

class ExperienceIntelligenceService:
    """
    Service responsible for converting candidate experiences into rich ExperienceIntelligence
    objects using LLM-based understanding.
    """
    
    _groq_chain = None

    @classmethod
    def _get_chains(cls):
        """Initializes and caches LLM chains globally to avoid redundant initialization overhead."""
        if cls._groq_chain is None:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """## Role
You are a Senior Engineering Hiring Manager conducting a work history review.

## Objective
Reconstruct what engineering work this person actually performed at this specific role. Extract only facts and directly observable activities. You are NOT evaluating the candidate. You are NOT scoring evidence.

## Schema Field Guidance

### `display_name`
Format: "Role @ Company" (e.g., "Software Engineer @ Google", "Backend Intern @ Startup XYZ")

### `company` and `role`
Extract exactly as stated.

### `work_type`
- If the title contains "Intern", "Internship", or "Trainee" → set to "INTERNSHIP"
- Otherwise → set to "EXPERIENCE"

### `domain` (KnowledgeDomain)
Same domain classification rules as Project Intelligence:
- "Software Engineering": Backend, frontend, full-stack, mobile, DevTools
- "AI/ML": Training models, building ML pipelines, autonomous agents
- Use "Unknown Engineering Domain" if the role description is too sparse to determine

**Anti-hallucination rules**: Same as Project Intelligence — using cloud services ≠ Cloud Computing, adding auth ≠ Cyber Security, etc.

### `duration`
Format as "Start Date - End Date" (e.g., "Jun 2024 - Dec 2024" or "Jan 2023 - Present").

### `achievements` (List of StructuredAchievement)
For every notable engineering action described in the work experience:
- `action`: e.g. "Implemented", "Optimized", "Designed", "Containerized"
- `technologies`: List of exact technologies involved
- `problem`: The engineering challenge or problem solved
- `solution`: The engineering solution implemented
- `impact`: The measurable or observable technical outcome (if explicitly stated, otherwise a direct factual outcome)

### `explicit_technologies`
Same rules as Project Intelligence. Extract only explicitly named tools. Concepts are NOT technologies.

### `engineering_capabilities`
Same canonical list as Project Intelligence. Extract observable engineering activities.

### `complexity`
- BEGINNER: Bug fixes, simple scripts, internal tools with no users
- INTERMEDIATE: Feature development, database work, standard deployments
- ADVANCED: System design, complex business logic, performance work, mentoring others
- PRODUCTION: High-traffic systems, architecture ownership, organization-wide impact

## Sparse Input Handling
If only Role, Company, and Duration exist with no description:
- Set `achievements` to empty list
- Set `engineering_capabilities` to empty list
- Set `explicit_technologies` to empty list (unless tech is in the job title, e.g., "Python Developer" → ["Python"])
- Set complexity to BEGINNER
- NEVER hallucinate achievements or technologies for sparse entries

## Constraints
- Populate every schema field
- Never invent achievements not described
- Never invent technologies not mentioned
- Never overestimate complexity
"""),
                ("user", """Here is the structured professional experience information:

{experience_context}

Synthesize one complete ExperienceIntelligence object from the structured experience information below.""")
            ])
            
            if settings.GROQ_API_KEY:
                llm = get_llm(
                    provider="groq",
                    model="llama-3.3-70b-versatile",
                    temperature=0,
                    max_tokens=8192
                )
                cls._groq_chain = prompt | llm.with_structured_output(ExperienceIntelligence)

        return cls._groq_chain

    @staticmethod
    async def analyze_experiences(experiences: List[ExperienceSchema]) -> List[ExperienceIntelligence]:
        """
        Takes a list of experiences and runs the LLM analysis on them concurrently.
        """
        import json
        print(f"\n[{'='*50}]")
        print("--> ENTERING STAGE: EXPERIENCE INTELLIGENCE AGENT")
        print("--> Input Experiences:")
        print(json.dumps([e.model_dump() for e in experiences], indent=2))

        if not experiences:
            print("--> Output Experience Intelligence: []")
            print(f"[{'='*50}]\n")
            return []
            
        results = []
        for exp in experiences:
            try:
                res = await ExperienceIntelligenceService.analyze_single_experience(exp)
                results.append(res)
            except Exception as e:
                results.append(e)
        
        valid_intelligence = []
        for res in results:
            if isinstance(res, ExperienceIntelligence):
                valid_intelligence.append(res)
            else:
                logger.error(f"Failed to analyze experience: {res}")
                
        print("--> Output Experience Intelligence:")
        print(json.dumps([item.model_dump() for item in valid_intelligence], indent=2))
        print(f"[{'='*50}]\n")

        return valid_intelligence

    @staticmethod
    async def analyze_single_experience(experience: ExperienceSchema) -> ExperienceIntelligence:
        """
        Executes the semantic extraction pipeline on a single experience.
        """
        groq_chain = ExperienceIntelligenceService._get_chains()
        
        # Serialize the entire experience context safely excluding missing/empty values
        experience_context_json = experience.model_dump_json(
            exclude_none=True, 
            exclude_unset=True, 
            exclude_defaults=True,
            indent=2
        )
            
        payload_vars = {
            "experience_context": experience_context_json
        }
        
        llm_result = None
        
        # Attempt 1: Groq (Llama-3)
        if groq_chain:
            try:
                from tenacity import retry, stop_after_attempt, wait_incrementing
                
                @retry(stop=stop_after_attempt(6), wait=wait_incrementing(start=15, increment=15, max=75), reraise=True)
                async def _invoke_groq():
                    return await groq_chain.ainvoke(payload_vars)
                    
                llm_result = await _invoke_groq()
            except Exception as e:
                logger.error(f"[Experience Intelligence] Groq failed: {e}.")
                
        if not llm_result:
            raise RuntimeError(f"All LLMs failed to analyze experience {experience.role or 'Unknown'}")
            
        return cast(ExperienceIntelligence, llm_result)
