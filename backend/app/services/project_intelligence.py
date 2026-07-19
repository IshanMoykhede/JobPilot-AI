import json
import logging
from typing import List, Dict
import asyncio

from app.core.llm_factory import get_llm
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
You are a Senior Engineering Hiring Manager conducting a technical portfolio review.

## Objective
Analyze a single candidate project and extract structured intelligence. You must extract only what is directly observable from the provided project description. You are NOT evaluating the candidate's overall ability. You are NOT scoring evidence quality.

## Schema Field Guidance

### `display_name`
Use the project title as-is. If no title exists, generate a concise 3-5 word descriptive name.

### `project_name`
The exact project title from the input.

### `project_type`
Classify into one of: "Web Application", "Mobile Application", "CLI Tool", "Library/SDK", "API Service", "Data Pipeline", "ML Model", "Desktop Application", "Browser Extension", "DevOps Tool", "Hardware Project", "Research Project", "Other".

### `domain` (KnowledgeDomain)
**Primary domain**: The single engineering discipline that best describes the core engineering work.
**Secondary domains**: Additional disciplines if the project genuinely spans multiple fields.

Domain classification rules:
- "Software Engineering": Web apps, APIs, CRUD systems, full-stack projects, developer tools, mobile apps
- "Artificial Intelligence / Machine Learning": Projects that train models, build neural networks, implement ML pipelines, or build autonomous agents with reasoning loops
- "Data Science": Projects focused on statistical analysis, data visualization, or data exploration
- "DevOps": Projects focused on CI/CD pipelines, infrastructure automation, container orchestration
- "Cloud Computing": Projects that architect cloud-native solutions (not just deploying to a cloud provider)
- "Embedded Systems": Projects involving microcontrollers, firmware, IoT devices
- Use "Unknown Engineering Domain" if genuinely unclear

**Anti-hallucination rules**:
- Using an API (e.g., OpenAI API, Stripe API) does NOT make a project AI/ML or FinTech
- Deploying to AWS/GCP does NOT make a project Cloud Computing
- Adding login/auth does NOT make a project Cyber Security
- Using Redis/message queues does NOT make a project Distributed Systems

### `explicit_technologies`
Extract every programming language, framework, library, database, cloud platform, infrastructure tool, and developer tool that is explicitly named in the project description.

**Include**: Python, JavaScript, TypeScript, React, Next.js, FastAPI, Django, Flask, Node.js, Express, PostgreSQL, MongoDB, Redis, Docker, Kubernetes, AWS, GCP, Firebase, Tailwind CSS, etc.
**Exclude**: Concepts and activities — "REST APIs", "Microservices", "Authentication", "OOP" are NOT technologies. These belong in `engineering_capabilities`.

### `engineering_capabilities`
Extract observable engineering activities demonstrated by the project. Use canonical names from this preferred list when applicable:

Backend Development, Frontend Development, Full-Stack Development, REST API Design, GraphQL API Design, Authentication, Authorization, Database Design, Caching, System Architecture, Performance Optimization, Deployment, Containerization, CI/CD, Real-time Systems, Payment Integration, Search Implementation, File Processing, Data Modeling, Testing, Monitoring, Agentic Workflows, Prompt Engineering, AI API Integration, CAD Modeling, PCB Design, Embedded Systems Programming, Structural Engineering, Project Management

If the project demonstrates a capability not on this list, use a concise 2-4 word descriptive name.

### `complexity`
- BEGINNER: Single-purpose script, tutorial clone, basic CRUD with no auth
- INTERMEDIATE: Multiple modules, authentication, database integration, external API usage
- ADVANCED: Multi-service architecture, caching layers, complex business logic, performance optimization
- PRODUCTION: Real users, deployed infrastructure, monitoring, CI/CD, handles real traffic

### `achievements` (List of StructuredAchievement)
For every notable engineering action described:
- `action`: e.g. "Implemented", "Optimized", "Designed", "Containerized"
- `technologies`: List of exact technologies involved
- `problem`: The engineering challenge or problem solved
- `solution`: The engineering solution implemented
- `impact`: The measurable or observable technical outcome (if explicitly stated, e.g., "45% reduction in read latency", otherwise a direct factual outcome)

### `architecture_tags`
List of observable architecture patterns (e.g., "RESTful", "Microservices", "Event-Driven", "Monolith"). Leave empty if not observable.

## Constraints
- Populate every schema field.
- Never invent technologies not mentioned in the input.
- Never invent capabilities not observable from described activities.
- When uncertain between two complexity levels, choose the lower one.
"""),
                ("user", """Here is the structured project information:

{project_context}

Synthesize one complete ProjectIntelligence object from the structured project information below.""")
            ])
            
            if settings.GROQ_API_KEY:
                llm = get_llm(
                    provider="groq",
                    model="llama-3.3-70b-versatile",
                    temperature=0,
                    max_tokens=8192
                )
                cls._groq_chain = prompt | llm.with_structured_output(ProjectIntelligence)

            if settings.GEMINI_API_KEY:
                gemini_llm = get_llm(
                    provider="gemini",
                    model="gemini-2.0-flash",
                    temperature=0
                )
                cls._gemini_chain = prompt | gemini_llm.with_structured_output(ProjectIntelligence)

        return cls._groq_chain, cls._gemini_chain
    
    @staticmethod
    async def analyze_projects(projects: List[ProjectSchema]) -> List[ProjectIntelligence]:
        """
        Takes a list of projects and runs the LLM analysis on them concurrently.
        """
        import json
        print(f"\n[{'='*50}]")
        print("--> ENTERING STAGE: PROJECT INTELLIGENCE AGENT")
        print("--> Input Projects:")
        print(json.dumps([p.model_dump() for p in projects], indent=2))

        if not projects:
            print("--> Output Project Intelligence: []")
            print(f"[{'='*50}]\n")
            return []
            
        results = []
        for proj in projects:
            try:
                res = await ProjectIntelligenceService.analyze_single_project(proj)
                results.append(res)
            except Exception as e:
                results.append(e)
        
        valid_intelligence = []
        for res in results:
            if isinstance(res, ProjectIntelligence):
                valid_intelligence.append(res)
            else:
                logger.error(f"Failed to analyze project: {res}")
                
        print("--> Output Project Intelligence:")
        print(json.dumps([item.model_dump() for item in valid_intelligence], indent=2))
        print(f"[{'='*50}]\n")

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
                from tenacity import retry, stop_after_attempt, wait_incrementing
                
                @retry(stop=stop_after_attempt(6), wait=wait_incrementing(start=15, increment=15, max=75), reraise=True)
                async def _invoke_groq():
                    return await groq_chain.ainvoke(payload_vars)
                    
                llm_result = await _invoke_groq()
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
