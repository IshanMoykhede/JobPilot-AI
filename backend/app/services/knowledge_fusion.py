import json
import logging
from typing import List

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import SecretStr
from typing import cast

from app.core.config import settings
from app.schemas.evidence import (
    ProjectIntelligence,
    ExperienceIntelligence,
    EducationIntelligence,
    CertificationIntelligence,
    UnifiedKnowledge
)

logger = logging.getLogger(__name__)

class KnowledgeFusionService:
    """
    LLM-powered semantic synthesis layer responsible for normalizing and aggregating
    evidence from all intelligence modules into a single UnifiedKnowledge model.
    """

    _groq_chain = None
    _gemini_chain = None

    @classmethod
    def _get_chains(cls):
        """Initializes and caches LLM chains globally to avoid redundant initialization overhead."""
        if cls._groq_chain is None and cls._gemini_chain is None:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """## Role
You are the Semantic Knowledge Fusion Layer of the Candidate Knowledge Engine.

## Objective
You are constructing the candidate's canonical engineering knowledge graph (UnifiedKnowledge). You will receive structured engineering intelligence extracted from multiple independent evidence sources. Your responsibility is to synthesize all evidence into one coherent UnifiedKnowledge representation.

## Strict Technology Normalization & Classification (CRITICAL):
- Semantically normalize synonymous technologies, frameworks, libraries, tools, and platforms into one canonical concept whenever the meaning is equivalent.
  - Examples: "ReactJS", "React.js" -> "React"; "NodeJS", "Node.js" -> "Node.js".
  - If a certification validates cloud learning (e.g. "AWS Academy Cloud Foundations"), extract "AWS" as the canonical technology (while leaving the certification name intact in certification evidence).
- Strictly map architectural concepts and activities to Capabilities, NEVER to Technologies.
  - Examples: "REST APIs" -> Capability ("REST API Design"); "JWT Authentication" -> Capability ("Authentication"); "Computer Networks" -> Capability or remove; "Object Oriented Programming" -> Capability.
  - If any of these are present as technologies in the input, remove them from the `technologies` array and merge them appropriately under `capabilities`.
- Do not duplicate equivalent technologies or capabilities. Represent them once and attach all supporting evidence.

## Rules for Evidence References
- `source_type`: Must be one of ["SKILL", "PROJECT", "EXPERIENCE", "EDUCATION", "CERTIFICATION"].
- `source_name`: The name of the project, company, degree, or "Resume Skills".
- `explicit`: true if it was explicitly stated, false if semantically inferred as a duplicate/merger.
- `occurrences`: The total number of evidence references for the item.

## Constraints
- You are a semantic synthesis layer, NOT an evaluator.
- Do NOT calculate confidence.
- Do NOT assign candidate strength or quality scores.
- Do NOT infer knowledge that is completely unsupported by the provided intelligence.
- Never lose useful engineering context.
- Output ONLY the UnifiedKnowledge JSON. No prose. No markdown. No explanations.
"""),
                ("user", """Here is the structured intelligence extracted from the candidate's resume:

### Resume Skills
{skills_context}

### Project Intelligence
{project_context}

### Experience Intelligence
{experience_context}

### Education Intelligence
{education_context}

### Certification Intelligence
{certification_context}

Synthesize ONE coherent UnifiedKnowledge graph based on all the evidence provided above.""")
            ])

            if settings.GROQ_API_KEY:
                llm = ChatGroq(
                    api_key=SecretStr(settings.GROQ_API_KEY),
                    model="llama-3.3-70b-versatile",
                    temperature=0
                )
                cls._groq_chain = prompt | llm.with_structured_output(UnifiedKnowledge)
                
            if settings.GEMINI_API_KEY:
                gemini_llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    api_key=SecretStr(settings.GEMINI_API_KEY),
                    temperature=0
                )
                cls._gemini_chain = prompt | gemini_llm.with_structured_output(UnifiedKnowledge)

        return cls._groq_chain, cls._gemini_chain

    @staticmethod
    async def fuse_knowledge(
        skills: List[str],
        project_intel: List[ProjectIntelligence],
        exp_intel: List[ExperienceIntelligence],
        edu_intel: List[EducationIntelligence],
        cert_intel: List[CertificationIntelligence]
    ) -> UnifiedKnowledge:
        """
        Takes raw skills and intelligence objects, serializes them, and calls the Fusion LLM.
        """
        groq_chain, gemini_chain = KnowledgeFusionService._get_chains()
        
        # Serialize payloads cleanly
        def serialize_list(intel_list):
            return json.dumps(
                [item.model_dump(exclude_none=True, exclude_defaults=True, exclude_unset=True) for item in intel_list],
                indent=2
            )

        payload_vars = {
            "skills_context": json.dumps(skills, indent=2),
            "project_context": serialize_list(project_intel),
            "experience_context": serialize_list(exp_intel),
            "education_context": serialize_list(edu_intel),
            "certification_context": serialize_list(cert_intel)
        }
        
        llm_result = None
        
        if groq_chain:
            try:
                llm_result = await groq_chain.ainvoke(payload_vars)
            except Exception as e:
                logger.error(f"[Knowledge Fusion] Groq failed: {e}. Falling back to Gemini.")
                
        if not llm_result and gemini_chain:
            try:
                llm_result = await gemini_chain.ainvoke(payload_vars)
            except Exception as e:
                logger.error(f"[Knowledge Fusion] Gemini failed: {e}.")
                
        if not llm_result:
            raise RuntimeError("All LLMs failed to fuse knowledge.")
            
        return cast(UnifiedKnowledge, llm_result)
