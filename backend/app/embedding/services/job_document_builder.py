from typing import List, Any
from app.job_search.models.job_knowledge import JobKnowledge

class JobDocumentBuilder:
    @staticmethod
    def build_document(job_knowledge: JobKnowledge) -> str:
        """
        Converts JobKnowledge into a deterministic semantic document text.
        Follows the strict Pipeline 3 formatting specification.
        Omits empty fields completely. Never hallucinates or infers data.
        """
        sections = []

        def add_section_string(title: str, value: Any):
            if value:
                val_str = str(value).strip()
                if val_str:
                    sections.append(f"{title}:\n{val_str}")

        def add_section_enum(title: str, enum_val: Any):
            if enum_val:
                val_str = str(enum_val.value if hasattr(enum_val, "value") else enum_val).strip()
                if val_str:
                    sections.append(f"{title}:\n{val_str}")

        def add_section_list(title: str, items: List[str]):
            if items and isinstance(items, list):
                cleaned = [str(item).strip() for item in items if str(item).strip()]
                if cleaned:
                    bullet_list = "\n".join([f"- {item}" for item in cleaned])
                    sections.append(f"{title}:\n{bullet_list}")
                    
        def add_section_int(title: str, value: Any, suffix: str = ""):
            if value is not None:
                try:
                    val_int = int(value)
                    sections.append(f"{title}:\n{val_int} {suffix}".strip())
                except ValueError:
                    pass

        # Deterministic Serialization Algorithm (Exact Ordering)
        
        # 1. Job Title
        add_section_string("Job Title", job_knowledge.job_title)
        
        # 2. Primary Domain
        add_section_enum("Primary Domain", job_knowledge.primary_domain)
        
        # 3. Secondary Domains
        add_section_list("Secondary Domains", job_knowledge.secondary_domains)
        
        # 4. Employment Level
        add_section_enum("Employment Level", job_knowledge.employment_level)
        
        # 5. Employment Type
        add_section_string("Employment Type", job_knowledge.employment_type)
        
        # 6. Work Mode
        add_section_string("Work Mode", job_knowledge.work_mode)
        
        # 7. Industry
        add_section_string("Industry", job_knowledge.industry)
        
        # 8. Required Technologies
        add_section_list("Required Technologies", job_knowledge.required_technologies)
        
        # 9. Preferred Technologies
        add_section_list("Preferred Technologies", job_knowledge.preferred_technologies)
        
        # 10. Required Capabilities
        add_section_list("Required Capabilities", job_knowledge.required_capabilities)
        
        # 11. Preferred Capabilities
        add_section_list("Preferred Capabilities", job_knowledge.preferred_capabilities)
        
        # 12. Required Certifications
        add_section_list("Required Certifications", job_knowledge.required_certifications)
        
        # 13. Preferred Certifications
        add_section_list("Preferred Certifications", job_knowledge.preferred_certifications)
        
        # 14. Minimum Experience
        add_section_int("Minimum Experience", job_knowledge.minimum_experience_years, "Years")
        
        # 15. Preferred Experience
        add_section_int("Preferred Experience", job_knowledge.preferred_experience_years, "Years")
        
        # 16. Required Degrees
        add_section_list("Required Degrees", job_knowledge.required_degrees)
        
        # 17. Preferred Degrees
        add_section_list("Preferred Degrees", job_knowledge.preferred_degrees)
        
        # 18. Required Specializations
        add_section_list("Required Specializations", job_knowledge.required_specializations)
        
        # 19. Preferred Specializations
        add_section_list("Preferred Specializations", job_knowledge.preferred_specializations)
        
        # 20. Responsibilities
        add_section_list("Responsibilities", job_knowledge.responsibilities)
        
        # 21. Benefits
        add_section_list("Benefits", job_knowledge.benefits)

        # Join all valid sections with double newlines
        return "\n\n".join(sections)
