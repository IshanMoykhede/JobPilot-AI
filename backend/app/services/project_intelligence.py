import json
import logging
from typing import List, Dict
import asyncio

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from app.core.config import settings
from app.schemas.candidate_profile import ProjectSchema
from app.schemas.evidence import ProjectIntelligence
from pydantic import SecretStr
from typing import cast

logger = logging.getLogger(__name__)

class ProjectIntelligenceService:
    """
    Service responsible for converting candidate projects into rich ProjectIntelligence
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
Your task is to analyze a candidate's project and extract structured semantic intelligence. You must ONLY extract facts and directly observable capabilities. You are NOT evaluating the candidate, nor are you scoring evidence.

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
- The summary MUST answer: What was built? How was it built? Why is it technically important?
- Maximum 2 sentences.
- Use professional recruiter language. Absolutely ban marketing or introduction phrases like "This project showcases...", "This project demonstrates...", or "The candidate built...".

## Extraction Workflow
Internal reasoning order:
1. Understand what the project actually builds.
2. Identify the engineering problem.
3. Identify the architecture.
4. Identify explicit technologies.
5. Identify engineering activities.
6. Map activities to EngineeringCapability.
7. Estimate complexity.
8. Produce the final summary.

Only after completing these internal steps populate the schema.

Step 1: Determine Project Domain. Classify based on the rules above.
Step 2: Understand Project Purpose. Extract the project type, challenges, scale, and architecture to populate `summary` and `display_name`.
Step 3: Estimate Complexity using the Complexity Rubric.
Step 4: Extract Explicit Technologies. Only extract tools strictly stated in the text. Do NOT infer or hallucinate.
Step 5: Extract Observable Engineering Capabilities. Select ONLY from the provided EngineeringCapability enum based on explicitly described activities. Never invent capability names. If none accurately describe the engineering work, return an empty capability list. Do not force mappings.

## Complexity Rubric
- BEGINNER: Single CRUD application, Tutorial clone, Small college project
- INTERMEDIATE: Multiple modules, Authentication, Database, API integration
- ADVANCED: Distributed architecture, Complex business logic, Caching, Scalability, Production practices
- PRODUCTION: Used by real users, Production deployment, Monitoring, CI/CD, Scaling, Multiple services, Real traffic

## Constraints
- Populate EVERY schema field.
- Never invent technologies.
- Never invent capabilities.
- Never invent engineering domains.
- Never infer unsupported facts.
- If two interpretations are possible, always choose the more conservative interpretation. Never overestimate candidate capability.

## Output Instructions
Return ONLY the ProjectIntelligence object JSON. No explanation. No markdown. No prose. Ensure `work_type` is set to "PROJECT"."""),
                ("user", """Here is the structured project information:

{project_context}

Synthesize one complete ProjectIntelligence object from the structured project information below.""")
            ])
            
            if settings.GROQ_API_KEY:
                llm = ChatGroq(
                    api_key=SecretStr(settings.GROQ_API_KEY),
                    model="llama-3.3-70b-versatile",
                    temperature=0
                )
                cls._groq_chain = prompt | llm.with_structured_output(ProjectIntelligence)

            if settings.GEMINI_API_KEY:
                gemini_llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    api_key=SecretStr(settings.GEMINI_API_KEY),
                    temperature=0
                )
                cls._gemini_chain = prompt | gemini_llm.with_structured_output(ProjectIntelligence)

        return cls._groq_chain, cls._gemini_chain
    
    @staticmethod
    async def analyze_projects(projects: List[ProjectSchema]) -> List[ProjectIntelligence]:
        """
        Takes a list of projects and runs the LLM analysis on them concurrently.
        """
        if not projects:
            return []
            
        tasks = [ProjectIntelligenceService.analyze_single_project(proj) for proj in projects]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_intelligence = []
        for res in results:
            if isinstance(res, ProjectIntelligence):
                valid_intelligence.append(res)
            else:
                logger.error(f"Failed to analyze project: {res}")
                
        return valid_intelligence

    @staticmethod
    async def analyze_single_project(project: ProjectSchema) -> ProjectIntelligence:
        """
        Executes the semantic extraction pipeline on a single project.
        """
        groq_chain, gemini_chain = ProjectIntelligenceService._get_chains()
        
        # Serialize the project context safely excluding empty/default fields
        project_context_json = project.model_dump_json(
            exclude_none=True, 
            exclude_unset=True, 
            exclude_defaults=True,
            indent=2
        )
            
        payload_vars = {
            "project_context": project_context_json
        }
        
        llm_result = None
        
        # Attempt 1: Groq (Llama-3)
        if groq_chain:
            try:
                llm_result = await groq_chain.ainvoke(payload_vars)
            except Exception as e:
                logger.error(f"[Project Intelligence] Groq failed: {e}. Falling back to Gemini.")
                
        # Attempt 2: Gemini Fallback
        if not llm_result and gemini_chain:
            try:
                llm_result = await gemini_chain.ainvoke(payload_vars)
            except Exception as e:
                logger.error(f"[Project Intelligence] Gemini failed: {e}.")
                
        if not llm_result:
            raise RuntimeError(f"All LLMs failed to analyze project {project.title or 'Unknown'}")
            
        return cast(ProjectIntelligence, llm_result)
