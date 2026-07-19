from typing import Union, Dict, Any, List

class CandidateDocumentBuilder:
    @staticmethod
    def build_document(candidate_knowledge: Union[Any, Dict[str, Any]]) -> str:
        """
        Converts CandidateKnowledge (Pydantic model or dict) into a deterministic semantic document text.
        Structure: Extracts only pure semantic fields directly from the public canonical collections.
        Empty fields are omitted entirely. Ordering is strict and deterministic.
        """
        if hasattr(candidate_knowledge, "model_dump"):
            data = candidate_knowledge.model_dump()
        else:
            data = candidate_knowledge or {}

        # 1. Map canonical objects
        identity = data.get("candidate_identity", {}) or {}
        level_data = data.get("candidate_level", {}) or {}
        edu_intel = data.get("education_intelligence", []) or []
        cert_intel = data.get("certification_intelligence", []) or []

        # 2. Extract values
        domains = identity.get("engineering_domains", []) or []
        domains_list = []
        for d in domains:
            if hasattr(d, "value"):
                domains_list.append(str(d.value))
            elif isinstance(d, dict) and "value" in d:
                domains_list.append(str(d["value"]))
            else:
                domains_list.append(str(d))
                
        primary_domain = domains_list[0] if domains_list else None
        secondary_domains = domains_list[1:] if len(domains_list) > 1 else []
        
        employment_level = level_data.get("title")
        total_months = level_data.get("total_months_experience")
        
        technologies = identity.get("technology_stack", []) or []
        capabilities = identity.get("strongest_capabilities", []) or []
        
        degrees = [edu.get("degree") for edu in edu_intel if isinstance(edu, dict) and edu.get("degree")]
        
        specializations = []
        if identity.get("primary_specialization"):
            specializations.append(identity.get("primary_specialization"))
        specializations.extend(identity.get("secondary_specializations", []) or [])
        
        certifications = [cert.get("certification_name") for cert in cert_intel if isinstance(cert, dict) and cert.get("certification_name")]
        ideal_roles = identity.get("ideal_roles", []) or []

        # 3. Serialization helpers
        sections = []

        def add_section_string(title: str, value: Any):
            if value:
                val_str = str(value).strip()
                if val_str:
                    sections.append(f"{title}:\n{val_str}")

        def add_section_list(title: str, items: List[Any]):
            if items and isinstance(items, list):
                cleaned = [str(item).strip() for item in items if str(item).strip()]
                if cleaned:
                    bullet_list = "\n".join([f"- {item}" for item in cleaned])
                    sections.append(f"{title}:\n{bullet_list}")
                    
        def add_section_months(title: str, value: Any):
            if value is not None:
                try:
                    val_int = int(value)
                    sections.append(f"{title}:\n{val_int} Months")
                except ValueError:
                    pass

        # 4. Deterministic Output Construction
        add_section_string("Primary Domain", primary_domain)
        add_section_list("Secondary Domains", secondary_domains)
        add_section_string("Employment Level", employment_level)
        add_section_months("Experience", total_months)
        add_section_list("Technologies", technologies)
        add_section_list("Capabilities", capabilities)
        add_section_list("Degrees", degrees)
        add_section_list("Specializations", specializations)
        add_section_list("Certifications", certifications)
        add_section_list("Ideal Roles", ideal_roles)

        return "\n\n".join(sections)
