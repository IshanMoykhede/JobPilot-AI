import json
import logging
from typing import List
import asyncio

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
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
    _gemini_chain = None

    @classmethod
    def _get_chains(cls):
        """Initializes and caches LLM chains globally to avoid redundant initialization overhead."""
        if cls._groq_chain is None and cls._gemini_chain is None:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """## Role
You are an expert Senior Technical Recruiter and Staff Engineering Manager.

## Objective
You are reconstructing what engineering work this person actually performed based on their professional experience. You must ONLY extract facts and directly observable capabilities. You are NOT evaluating the candidate, nor are you scoring evidence.

## Technology vs. Capability Distinction (CRITICAL):
- Classify Programming Languages, Frameworks, Libraries, Databases, Cloud Platforms, Infrastructure, and Developer Tools as TECHNOLOGIES (e.g. Python, React, FastAPI, Docker, PostgreSQL, Redis).
- Classify Activities and Processes as CAPABILITIES (e.g. REST API Design, Authentication, Authorization, Database Design, Performance Optimization, System Architecture, Caching, Deployment).
- NEVER classify architectural concepts or general engineering topics (such as "REST APIs", "JWT Authentication", "Computer Networks", or "Object Oriented Programming") as technologies. Treat them as capabilities (e.g. "REST API Design", "Authentication") or general topics, or exclude them if they do not fit the schema enums.

## Domain Safety & Hallucination Reduction (CRITICAL):
- Assign engineering domains ONLY when the candidate's primary engineering work clearly belongs to that domain.
- Do NOT infer domains from adjectives such as "secure" (does NOT mean Cyber Security), "distributed" (does NOT mean Distributed Systems), "scalable" or "cloud-ready" (does NOT mean Cloud Computing), or "AI-powered" (does NOT mean AI/ML unless they built model architectures/agents directly).
- Examples: Security features != Cyber Security; Cloud deployment != Cloud Computing; OpenAI API usage != AI Engineering; Redis != Distributed Systems.
- Always prefer conservative domain classification. If unsure, use UNKNOWN_ENGINEERING_DOMAIN.

## Recruiter Summary Styling (CRITICAL):
- The summary MUST answer: What was built/done? How was it built/done? Why is it technically important?
- Maximum 2 sentences.
- Use professional recruiter language. Absolutely ban marketing or introduction phrases like "This project showcases...", "This experience demonstrates...", or "The candidate...".

## Extraction Workflow
Internal reasoning order:
1. Understand the role.
2. Determine the engineering team (e.g., Backend, Frontend, Platform, DevOps, AI, Cloud, Security, etc.).
3. Determine the engineering problems solved.
4. Determine daily responsibilities.
5. Determine engineering activities.
6. Map activities to descriptive Engineering Capabilities.
7. Extract explicit technologies.
8. Estimate engineering complexity.
9. Write recruiter summary.

Only after completing these internal steps populate the schema.

Step 1: Determine Experience Domain. Classify based on the rules above.
Step 2: Understand Experience Purpose. Extract normalized responsibilities and populate `summary` and `display_name` (e.g., 'Role @ Company').
Step 3: Estimate Complexity using the Complexity Rubric.
Step 4: Extract Explicit Technologies. Only extract tools strictly stated in the text. Do NOT infer or hallucinate.
Step 5: Extract Observable Engineering Capabilities. Select ONLY from the provided EngineeringCapability enum based on explicitly described activities. Never invent capability names. If none accurately describe the engineering work, return an empty capability list. Do not force mappings.

## Responsibilities Extraction
Normalize noisy resume descriptions into clean engineering intelligence. Responsibilities should represent engineering work, not resume wording.
Examples:
- "Developed REST APIs using FastAPI" -> "Designed and implemented REST APIs"
- "Worked on deployment" -> "Managed application deployment"
- "Optimized SQL queries" -> "Optimized database performance"

## Capability Mapping
Engineering Capability represents an engineering activity, not a technology.
First identify the engineering work performed.
Then map that work into the closest EngineeringCapability already defined in the schema.

Examples:
- Designing APIs -> REST_API_DESIGN
- Managing authentication -> AUTHENTICATION
- Designing HVAC systems -> THERMODYNAMICS_DESIGN
- Developing printed circuit boards -> PCB_DESIGN
- Analyzing soil for foundations -> GEOTECHNICAL_ANALYSIS
- Scaling up chemical production -> CHEMICAL_PROCESS_SCALING

If no existing capability accurately represents the work, leave the capability list empty.
Never invent new capability names.
Never force an incorrect mapping.

## Sparse Experience Handling
If only Role, Company, and Duration exist (the description is sparse or missing):
- Extract ONLY the domain, display_name, role, company, conservative summary, and explicit technologies (if present in the title).
- Return empty capability lists rather than hallucinating.
- Always prefer under-classification over over-classification.

## Complexity Rubric
- BEGINNER: Basic bug fixes, simple scripts, internal tools with no scale
- INTERMEDIATE: Feature development, database integrations, standard deployments
- ADVANCED: Distributed architecture, Complex business logic, Caching, Scalability, Production practices, Mentorship
- PRODUCTION: High traffic systems, Mission-critical infrastructure, Architecture ownership, Organization-wide impact

## Constraints
- Think internally.
- Follow the reasoning sequence.
- Populate every schema field.
- Never invent responsibilities.
- Never invent technologies.
- Never invent engineering capabilities.
- Never overestimate candidate expertise.
- Prefer conservative interpretation.

## Output Instructions
Return ONLY the ExperienceIntelligence object JSON. No explanation. No markdown. No prose. Ensure `work_type` is set to "EXPERIENCE".
"""),
                ("user", """Here is the structured professional experience information:

{experience_context}

Synthesize one complete ExperienceIntelligence object from the structured experience information below.""")
            ])
            
            if settings.GROQ_API_KEY:
                llm = ChatGroq(
                    api_key=SecretStr(settings.GROQ_API_KEY),
                    model="llama-3.3-70b-versatile",
                    temperature=0
                )
                cls._groq_chain = prompt | llm.with_structured_output(ExperienceIntelligence)
                
            if settings.GEMINI_API_KEY:
                gemini_llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    api_key=SecretStr(settings.GEMINI_API_KEY),
                    temperature=0
                )
                cls._gemini_chain = prompt | gemini_llm.with_structured_output(ExperienceIntelligence)

        return cls._groq_chain, cls._gemini_chain

    @staticmethod
    async def analyze_experiences(experiences: List[ExperienceSchema]) -> List[ExperienceIntelligence]:
        """
        Takes a list of experiences and runs the LLM analysis on them concurrently.
        """
        if not experiences:
            return []
            
        tasks = [ExperienceIntelligenceService.analyze_single_experience(exp) for exp in experiences]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_intelligence = []
        for res in results:
            if isinstance(res, ExperienceIntelligence):
                valid_intelligence.append(res)
            else:
                logger.error(f"Failed to analyze experience: {res}")
                
        return valid_intelligence

    @staticmethod
    async def analyze_single_experience(experience: ExperienceSchema) -> ExperienceIntelligence:
        """
        Executes the semantic extraction pipeline on a single experience.
        """
        groq_chain, gemini_chain = ExperienceIntelligenceService._get_chains()
        
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
                llm_result = await groq_chain.ainvoke(payload_vars)
            except Exception as e:
                logger.error(f"[Experience Intelligence] Groq failed: {e}. Falling back to Gemini.")
                
        # Attempt 2: Gemini Fallback
        if not llm_result and gemini_chain:
            try:
                llm_result = await gemini_chain.ainvoke(payload_vars)
            except Exception as e:
                logger.error(f"[Experience Intelligence] Gemini failed: {e}.")
                
        if not llm_result:
            raise RuntimeError(f"All LLMs failed to analyze experience {experience.role or 'Unknown'}")
            
        return cast(ExperienceIntelligence, llm_result)
