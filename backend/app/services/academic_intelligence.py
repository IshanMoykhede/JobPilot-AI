import logging
import asyncio
from typing import List

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from app.core.config import settings
from app.schemas.candidate_profile import EducationSchema, CertificationSchema
from app.schemas.evidence import EducationIntelligence, CertificationIntelligence
from pydantic import SecretStr
from typing import cast

logger = logging.getLogger(__name__)

class AcademicIntelligenceService:
    """
    Service responsible for converting candidate academic history and credentials 
    into rich BaseAcademicIntelligence objects using LLM-based understanding.
    """

    _groq_chain_edu = None
    _gemini_chain_edu = None
    _groq_chain_cert = None
    _gemini_chain_cert = None

    @classmethod
    def _get_chains(cls):
        """Initializes and caches LLM chains globally to avoid redundant initialization overhead."""
        if cls._groq_chain_edu is None:
            # Education Prompt
            edu_prompt = ChatPromptTemplate.from_messages([
                ("system", """## Role
You are an expert Senior Engineering Recruiter.
You recruit candidates across multiple engineering disciplines.
Your job is to understand engineering education irrespective of engineering discipline.

## Objective
You are reconstructing what academic foundation this degree provides. You must ONLY extract facts and observable academic exposure. You are NOT evaluating the candidate, nor are you scoring evidence.

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
- The summary MUST answer: What was built/studied? How was it built/studied? Why is it technically important?
- Maximum 2 sentences.
- Use professional recruiter language. Absolutely ban marketing or introduction phrases like "This project showcases...", "This degree demonstrates...", or "The candidate...".

## Extraction Workflow
Internal reasoning order:
1. Understand the engineering discipline.
2. Determine the academic specialization.
3. Determine the theoretical foundations.
4. Identify explicitly mentioned technologies only.
5. Identify observable academic capabilities.
6. Write a concise recruiter summary.

Only after completing these internal steps populate the schema.

## Education Extraction Philosophy
- Never infer production experience.
- Never infer internships.
- Never infer practical mastery.
- Never infer commercial exposure.
- Never infer tools simply because they are commonly taught.
- Never assume React, Docker, AWS, Python, etc. unless explicitly present.
The output should describe academic exposure only.

## Capability Mapping
Engineering Capability represents an engineering activity, not a technology.
Select ONLY from the provided EngineeringCapability enum based on explicitly described coursework/projects. Never invent capability names. If none accurately describe the academic exposure, return an empty capability list. Do not force mappings.

## Sparse Input Handling
If only Degree and University exist:
- Return only what can genuinely be extracted (domain, display_name, university, conservative summary).
- Leave capability lists empty.
- Prefer under-classification over hallucination.

## Conservative Philosophy
Never invent. Never exaggerate. Never over-classify. Prefer returning less information over incorrect information.

## Output Instructions
Return ONLY the EducationIntelligence object JSON. No explanation. No markdown. No prose.
"""),
                ("user", """Here is the structured education information:

{education_context}

Synthesize one complete EducationIntelligence object from the structured information below.""")
            ])

            # Certification Prompt
            cert_prompt = ChatPromptTemplate.from_messages([
                ("system", """## Role
You are an expert Senior Engineering Recruiter.
You recruit candidates across multiple engineering disciplines.
Your job is to understand engineering certifications irrespective of engineering discipline.

## Objective
You are reconstructing what knowledge this certification validates. You must ONLY extract facts. You are NOT evaluating the candidate.

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
- The summary MUST answer: What was built/validated? How was it built/validated? Why is it technically important?
- Maximum 2 sentences.
- Use professional recruiter language. Absolutely ban marketing or introduction phrases like "This certification showcases...", "This credential demonstrates...", or "The candidate...".

## Extraction Workflow
Internal reasoning order:
1. Understand certification ecosystem.
2. Determine engineering discipline.
3. Identify explicitly mentioned technologies.
4. Determine validated engineering capabilities.
5. Produce recruiter summary.

Only after completing these internal steps populate the schema.

## Certification Extraction Philosophy
A certification validates learning.
- It does NOT prove production experience.
- It does NOT prove mastery.
- It does NOT prove years of expertise.
Avoid over-classification.

## Capability Mapping
Engineering Capability represents an engineering activity, not a technology.
Select ONLY from the provided EngineeringCapability enum based on explicitly validated skills. Never invent capability names. If none accurately describe the validation, return an empty capability list. Do not force mappings.

## Sparse Input Handling
If only Name and Issuer exist:
- Return only what can genuinely be extracted.
- Leave capability lists empty.
- Prefer under-classification over hallucination.

## Conservative Philosophy
Never invent. Never exaggerate. Never over-classify. Prefer returning less information over incorrect information.

## Output Instructions
Return ONLY the CertificationIntelligence object JSON. No explanation. No markdown. No prose.
"""),
                ("user", """Here is the structured certification information:

{certification_context}

Synthesize one complete CertificationIntelligence object from the structured information below.""")
            ])

            if settings.GROQ_API_KEY:
                llm = ChatGroq(
                    api_key=SecretStr(settings.GROQ_API_KEY),
                    model="llama-3.3-70b-versatile",
                    temperature=0
                )
                cls._groq_chain_edu = edu_prompt | llm.with_structured_output(EducationIntelligence)
                cls._groq_chain_cert = cert_prompt | llm.with_structured_output(CertificationIntelligence)
                
            if settings.GEMINI_API_KEY:
                gemini_llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash",
                    api_key=SecretStr(settings.GEMINI_API_KEY),
                    temperature=0
                )
                cls._gemini_chain_edu = edu_prompt | gemini_llm.with_structured_output(EducationIntelligence)
                cls._gemini_chain_cert = cert_prompt | gemini_llm.with_structured_output(CertificationIntelligence)

        return cls._groq_chain_edu, cls._gemini_chain_edu, cls._groq_chain_cert, cls._gemini_chain_cert

    # ---------------------------------------------------------
    # EDUCATION INTELLIGENCE
    # ---------------------------------------------------------
    @staticmethod
    async def analyze_education(educations: List[EducationSchema]) -> List[EducationIntelligence]:
        if not educations:
            return []
            
        tasks = [AcademicIntelligenceService.analyze_single_education(edu) for edu in educations]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_intelligence = []
        for res in results:
            if isinstance(res, EducationIntelligence):
                valid_intelligence.append(res)
            else:
                logger.error(f"Failed to analyze education: {res}")
                
        return valid_intelligence

    @staticmethod
    async def analyze_single_education(education: EducationSchema) -> EducationIntelligence:
        groq_chain, gemini_chain, _, _ = AcademicIntelligenceService._get_chains()
        
        # Serialize entire schema
        education_context = education.model_dump_json(
            exclude_none=True,
            exclude_defaults=True,
            exclude_unset=True,
            indent=2
        )
        
        payload_vars = {"education_context": education_context}
        llm_result = None
        
        if groq_chain:
            try:
                llm_result = await groq_chain.ainvoke(payload_vars)
            except Exception as e:
                logger.error(f"[Education Intelligence] Groq failed: {e}. Falling back to Gemini.")
                
        if not llm_result and gemini_chain:
            try:
                llm_result = await gemini_chain.ainvoke(payload_vars)
            except Exception as e:
                logger.error(f"[Education Intelligence] Gemini failed: {e}.")
                
        if not llm_result:
            raise RuntimeError("All LLMs failed to analyze education.")
            
        return llm_result

    # ---------------------------------------------------------
    # CERTIFICATION INTELLIGENCE
    # ---------------------------------------------------------
    @staticmethod
    async def analyze_certifications(certifications: List[CertificationSchema]) -> List[CertificationIntelligence]:
        if not certifications:
            return []
            
        tasks = [AcademicIntelligenceService.analyze_single_certification(cert) for cert in certifications]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_intelligence = []
        for res in results:
            if isinstance(res, CertificationIntelligence):
                valid_intelligence.append(res)
            else:
                logger.error(f"Failed to analyze certification: {res}")
                
        return valid_intelligence

    @staticmethod
    async def analyze_single_certification(certification: CertificationSchema) -> CertificationIntelligence:
        _, _, groq_chain, gemini_chain = AcademicIntelligenceService._get_chains()
        
        # Serialize entire schema
        certification_context = certification.model_dump_json(
            exclude_none=True,
            exclude_defaults=True,
            exclude_unset=True,
            indent=2
        )
        
        payload_vars = {"certification_context": certification_context}
        llm_result = None
        
        if groq_chain:
            try:
                llm_result = await groq_chain.ainvoke(payload_vars)
            except Exception as e:
                logger.error(f"[Certification Intelligence] Groq failed: {e}. Falling back to Gemini.")
                
        if not llm_result and gemini_chain:
            try:
                llm_result = await gemini_chain.ainvoke(payload_vars)
            except Exception as e:
                logger.error(f"[Certification Intelligence] Gemini failed: {e}.")
                
        if not llm_result:
            raise RuntimeError("All LLMs failed to analyze certification.")
            
        return llm_result
