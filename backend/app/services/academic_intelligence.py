import logging
import asyncio
from typing import List

from app.core.llm_factory import get_llm
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
                ("system", """## ROLE
You are a Senior Engineering Academic Intelligence Agent.

Your responsibility is to analyze ONE academic qualification and extract structured facts.

Identify:
- degree: The name of the degree (e.g., "B.Tech", "M.S.", "Bachelor of Engineering")
- university: The name of the college, university, or institution
- specialization: The major or field of study (e.g., "Computer Science", "Mechanical Engineering")
- cgpa: Cumulative GPA or grade percentage if explicitly stated (as a float, e.g. 8.5 or 3.8). Return null if not stated.
- graduation_year: The year of completion or graduation if explicitly stated (as an integer, e.g. 2025). Return null if not stated.

## Strict Rules
- Never invent information not present in the input.
- Return ONLY the EducationIntelligence JSON object.
"""),
                ("user", """Here is the structured education information:

{education_context}

Synthesize one complete EducationIntelligence object from the structured information below.""")
            ])

            # Certification Prompt
            cert_prompt = ChatPromptTemplate.from_messages([
                ("system", """## ROLE
You are a Senior Engineering Certification Intelligence Agent.

Your responsibility is to analyze ONE professional certification and extract structured facts.

Identify:
- certification_name: The name of the certification (e.g., "AWS Certified Developer – Associate")
- issuing_organization: The organization that issued it (e.g., "Amazon Web Services")
- completion_date: The date or year of completion if explicitly stated (as a string, e.g. "Oct 2025"). Return null if not stated.
- technologies: List of exact technologies explicitly validated by the certification (e.g. `["AWS", "Docker"]`). Do not invent.
- capabilities: List of exact capabilities explicitly validated by the certification (e.g. `["Cloud Architecture"]`). Do not invent.

## Strict Rules
- Never invent information not present in the input.
- Return ONLY the CertificationIntelligence JSON object.
"""),
                ("user", """Here is the structured certification information:

{certification_context}

Synthesize one complete CertificationIntelligence object from the structured information below.""")
            ])

            if settings.GROQ_API_KEY:
                llm = get_llm(
                    provider="groq",
                    model="llama-3.3-70b-versatile",
                    temperature=0,
                    max_tokens=8192
                )
                cls._groq_chain_edu = edu_prompt | llm.with_structured_output(EducationIntelligence)
                cls._groq_chain_cert = cert_prompt | llm.with_structured_output(CertificationIntelligence)
                
            if settings.GEMINI_API_KEY:
                gemini_llm = get_llm(
                    provider="gemini",
                    model="gemini-2.0-flash",
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
        import json
        print(f"\n[{'='*50}]")
        print("--> ENTERING STAGE: ACADEMIC EDUCATION INTELLIGENCE EXTRACTION")
        print("--> Input Educations:")
        print(json.dumps([e.model_dump() for e in educations], indent=2))

        if not educations:
            print("--> Output Education Intelligence: []")
            print(f"[{'='*50}]\n")
            return []
            
        results = []
        for edu in educations:
            try:
                res = await AcademicIntelligenceService.analyze_single_education(edu)
                results.append(res)
            except Exception as e:
                results.append(e)
        
        valid_intelligence = []
        for res in results:
            if isinstance(res, EducationIntelligence):
                valid_intelligence.append(res)
            else:
                logger.error(f"Failed to analyze education: {res}")
                
        print("--> Output Education Intelligence:")
        print(json.dumps([item.model_dump() for item in valid_intelligence], indent=2))
        print(f"[{'='*50}]\n")

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
                from tenacity import retry, stop_after_attempt, wait_incrementing
                
                @retry(stop=stop_after_attempt(6), wait=wait_incrementing(start=15, increment=15, max=75), reraise=True)
                async def _invoke_groq():
                    return await groq_chain.ainvoke(payload_vars)
                    
                llm_result = await _invoke_groq()
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
        import json
        print(f"\n[{'='*50}]")
        print("--> ENTERING STAGE: ACADEMIC CERTIFICATION INTELLIGENCE EXTRACTION")
        print("--> Input Certifications:")
        print(json.dumps([c.model_dump() for c in certifications], indent=2))

        if not certifications:
            print("--> Output Certification Intelligence: []")
            print(f"[{'='*50}]\n")
            return []
            
        results = []
        for cert in certifications:
            try:
                res = await AcademicIntelligenceService.analyze_single_certification(cert)
                results.append(res)
            except Exception as e:
                results.append(e)
        
        valid_intelligence = []
        for res in results:
            if isinstance(res, CertificationIntelligence):
                valid_intelligence.append(res)
            else:
                logger.error(f"Failed to analyze certification: {res}")
                
        print("--> Output Certification Intelligence:")
        print(json.dumps([item.model_dump() for item in valid_intelligence], indent=2))
        print(f"[{'='*50}]\n")

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
                from tenacity import retry, stop_after_attempt, wait_incrementing
                
                @retry(stop=stop_after_attempt(6), wait=wait_incrementing(start=15, increment=15, max=75), reraise=True)
                async def _invoke_groq():
                    return await groq_chain.ainvoke(payload_vars)
                    
                llm_result = await _invoke_groq()
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
