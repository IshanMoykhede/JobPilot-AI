import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.config import settings
from app.schemas.candidate_profile import CompleteOnboardingRequest, ExperienceSchema
from app.schemas.evidence import (
    CandidateEvidence, CandidateLevel, CandidateMaturity,
    SkillEvidenceItem, EvidenceSummary, DomainClassification
)
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_insights import CandidateInsights, InsightStatus

class EvidenceEngineService:
    """
    This is a "Service" class. In backend development, we use Service classes to group
    all the complex business logic (the "math" and "thinking" of the app) into one place.
    By using @staticmethod, we can call these functions directly like EvidenceEngineService.build_candidate_evidence()
    without having to create an "instance" of the class first.
    """

    @staticmethod
    def build_candidate_evidence(profile_data: CompleteOnboardingRequest) -> CandidateEvidence:
        """
        This is the main "manager" function. You give it the raw profile data, 
        and it delegates the work to all the smaller helper functions below.
        """
        # 1. Grab the resume data and the user's preferences from the input
        candidate_resume = profile_data.resume_data
        candidate_preferences = profile_data.preferences
        
        # 2. Call our helper functions one by one to calculate the evidence
        skill_evidence_dict = EvidenceEngineService._calculate_skill_evidence(candidate_resume)
        candidate_level = EvidenceEngineService._calculate_candidate_level(candidate_resume.experience)
        candidate_maturity = EvidenceEngineService._calculate_candidate_maturity(candidate_resume)
        domain_class = EvidenceEngineService._detect_domains(candidate_resume, candidate_preferences)
        summary = EvidenceEngineService._generate_summary(skill_evidence_dict)
        
        # 3. Bundle everything together into our final Pydantic schema and return it
        return CandidateEvidence(
            candidate_level=candidate_level,
            candidate_maturity=candidate_maturity,
            current_domains=domain_class.current_domains,
            target_domains=domain_class.target_domains,
            skill_evidence=skill_evidence_dict,
            evidence_summary=summary,
            project_complexity=None  # We leave this empty for now, to be built in V2
        )

    @staticmethod
    def persist_evidence(db: Session, profile: CandidateProfile, evidence: CandidateEvidence) -> CandidateInsights:
        """
        This function saves our calculated evidence into the PostgreSQL database.
        """
        # First, we check if the user already has insights saved in the database.
        # profile.insights is a relationship to the CandidateInsights table.
        if profile.insights:
            # We are using a 1:Many relationship, so we want to create a NEW snapshot
            # every time this runs to track historical progress.
            insight = CandidateInsights(
                candidate_profile_id=profile.id,
                status=InsightStatus.COMPLETED,
                generated_at=datetime.utcnow()
            )
            db.add(insight)
        else:
            # If this is their very first time, create their first insight row
            insight = CandidateInsights(
                candidate_profile_id=profile.id,
                status=InsightStatus.COMPLETED,
                generated_at=datetime.utcnow()
            )
            db.add(insight)
        
        # We store the evidence inside the 'insights_json' column, specifically under
        # the 'evidence_engine' key so it doesn't mix with future data like market research.
        # 'evidence.model_dump()' converts our Pydantic object into a standard Python dictionary.
        current_json = insight.insights_json or {}
        current_json["evidence_engine"] = evidence.model_dump()
        insight.insights_json = current_json
        
        # Save the changes to the database
        db.commit()
        db.refresh(insight)
        
        return insight

    @staticmethod
    def _calculate_skill_evidence(resume) -> Dict[str, SkillEvidenceItem]:
        """
        This calculates how many 'points' a candidate gets for each skill based on where
        it was found in their resume.
        """
        # This dictionary will hold the skill name as the key, and its score/sources as the value.
        evidence_map: Dict[str, dict] = {}
        
        # This is a "nested function" or "helper function" used only inside this method
        # to avoid repeating the exact same lines of code 4 times below.
        def add_evidence(skill: str, points: int, source: str):
            # Convert the skill to lowercase and remove extra spaces so 'Python' and ' python ' match
            clean_skill = skill.lower().strip()
            if not clean_skill:
                return  # If it's empty, do nothing
                
            # If this is the first time we see this skill, set it up in our dictionary
            if clean_skill not in evidence_map:
                evidence_map[clean_skill] = {"score": 0, "sources": []}
                
            # Add the points and record where we found it
            evidence_map[clean_skill]["score"] += points
            evidence_map[clean_skill]["sources"].append(source)

        # 1. Look through the skills list (+1 point)
        for skill in resume.skills:
            add_evidence(skill, 1, "skills_list")

        # 2. Look through certifications (+2 points)
        for cert in resume.certifications:
            if cert.name: 
                add_evidence(cert.name, 2, f"certification: {cert.name}")

        # 3. Look through projects (+3 points)
        for project in resume.projects:
            for tech in project.technologies:
                # We use 'or' here. If project.title is None, it defaults to 'Unknown'
                project_title = project.title or "Unknown"
                add_evidence(tech, 3, f"project: {project_title}")

        # 4. Look through experience (+5 points)
        for job in resume.experience:
            if job.description:
                job_description = job.description.lower()
                
                # We loop through all the skills we ALREADY found to see if they are
                # mentioned in the job description.
                # 'list(evidence_map.keys())' gives us an array of skill names.
                for claimed_skill in list(evidence_map.keys()):
                    if claimed_skill in job_description:
                        job_role = job.role or "Unknown Role"
                        job_company = job.company or "Unknown Company"
                        source_label = f"experience: {job_role} at {job_company}"
                        
                        # Only add the points if we haven't already counted this exact job for this skill
                        if source_label not in evidence_map[claimed_skill]["sources"]:
                            add_evidence(claimed_skill, 5, source_label)

        # Now we convert our raw dictionary into nice structured Pydantic objects
        final_result = {}
        # .items() lets us loop over both the key (skill_name) and the value (skill_data) at the same time
        for skill_name, skill_data in evidence_map.items():
            total_score = skill_data["score"]
            
            # Determine the 'tier' based on the score
            if total_score >= 8: 
                tier = "Demonstrated"
            elif total_score >= 3: 
                tier = "Applied"
            else: 
                tier = "Claimed"
                
            final_result[skill_name] = SkillEvidenceItem(
                total_score=total_score, 
                tier=tier, 
                sources=skill_data["sources"]
            )
            
        return final_result

    @staticmethod
    def _calculate_candidate_level(experience_list: List[ExperienceSchema]) -> CandidateLevel:
        """
        This calculates the total number of months the person has worked to determine
        if they are a Fresher, Junior, Mid-Level, or Senior.
        """
        total_months_worked = 0
        current_date = datetime.now()
        
        for job in experience_list:
            # If they didn't list a start date, we can't calculate time, so we skip this job
            if not job.start_date: 
                continue
            
            # Try to parse dates like "2022-05". 
            # We use a try/except block because users type messy dates on resumes.
            # If the code inside 'try' crashes, it jumps to 'except' instead of breaking the app.
            try:
                # .split("-") turns "2022-05" into a list ["2022", "05"]
                start_parts = job.start_date.split("-")
                start_year = int(start_parts[0])
                # If there is no month provided, we just default to month 1 (January)
                start_month = int(start_parts[1]) if len(start_parts) > 1 else 1
                start_datetime = datetime(start_year, start_month, 1)
                
                # Assume the end date is today, unless they provided a specific end date
                end_datetime = current_date
                if job.end_date and job.end_date.lower() != "present":
                    end_parts = job.end_date.split("-")
                    end_year = int(end_parts[0])
                    end_month = int(end_parts[1]) if len(end_parts) > 1 else 1
                    end_datetime = datetime(end_year, end_month, 1)
                
                # Calculate the difference in months
                months = (end_datetime.year - start_datetime.year) * 12 + (end_datetime.month - start_datetime.month)
                
                # Only add if it's a positive number (in case dates were typed backwards)
                if months > 0:
                    total_months_worked += months
                    
            except Exception:
                # If date parsing fails, we just 'pass' (do nothing) and move to the next job
                pass 
                
        # Assign the title based on total months
        if total_months_worked < 18: 
            title = "Fresher"
        elif total_months_worked < 36: 
            title = "Junior"
        elif total_months_worked < 84: 
            title = "Mid-Level"
        else: 
            title = "Senior"
        
        return CandidateLevel(title=title, total_months_experience=total_months_worked)

    @staticmethod
    def _calculate_candidate_maturity(resume) -> CandidateMaturity:
        """
        This calculates signs of 'hustle', especially important for Freshers.
        """
        total_internships = 0
        
        for job in resume.experience:
            # We check if 'intern' is in their job title.
            # We convert to lowercase first so 'Intern' and 'intern' both match.
            if job.role and "intern" in job.role.lower():
                total_internships += 1
                
        return CandidateMaturity(
            project_count=len(resume.projects),         # len() counts items in a list
            certification_count=len(resume.certifications),
            internship_count=total_internships
        )

    @staticmethod
    def _generate_summary(skill_evidence_dict: Dict[str, SkillEvidenceItem]) -> EvidenceSummary:
        """
        Creates a quick high-level summary of the skill tiers.
        """
        demonstrated_count = 0
        claimed_count = 0
        
        # .values() loops through just the SkillEvidenceItem objects inside the dictionary
        for skill_data in skill_evidence_dict.values():
            if skill_data.tier == "Demonstrated": 
                demonstrated_count += 1
            if skill_data.tier == "Claimed": 
                claimed_count += 1
                
        return EvidenceSummary(
            total_skills_detected=len(skill_evidence_dict),
            demonstrated_skills_count=demonstrated_count,
            claimed_only_skills_count=claimed_count
        )

    @staticmethod
    def _detect_domains(resume, prefs) -> DomainClassification:
        """
        This is the ONLY part of this engine that uses AI.
        It asks an LLM to categorize the candidate's industry (e.g. Backend Development, Marketing).
        """
        # .join() combines a list of words into a single string, separated by commas.
        skills_text = ", ".join(resume.skills)
        preferred_roles_text = ", ".join(prefs.preferred_roles)
        
        # We use a list comprehension here. It's a faster way to write a for loop in Python.
        # It creates a list of strings formatted like "Title: Description" for each project.
        projects_text = "; ".join([f"{project.title}: {project.description or ''}" for project in resume.projects])
        experience_text = "; ".join([f"{job.role} at {job.company}" for job in resume.experience])
        
        # This is an f-string (formatted string). Notice the 'f' at the start.
        # It lets us inject variables directly into the text using {variable_name}.
        prompt = f"""You are a Career Domain Classifier. Given the following candidate profile, categorize their industry domains.
Return a valid JSON object matching this schema exactly:
{{
  "current_domains": ["string", ...],
  "target_domains": ["string", ...]
}}

Input:
Skills: {skills_text}
Projects: {projects_text}
Experience: {experience_text}
Preferred Roles (Target): {preferred_roles_text}

Rules:
1. "current_domains" are domains inferred from Skills, Projects, and Experience (e.g. "Backend Engineering", "Data Science", "Digital Marketing"). Limit to 1-3.
2. "target_domains" are inferred from Preferred Roles. Limit to 1-3.
3. Keep domain names standard and broad.
4. Output ONLY raw JSON. No markdown, no text.
"""
        try:
            # We try Groq first because it's usually faster. If not available, we use Gemini.
            if settings.GROQ_API_KEY:
                raw_json_response = EvidenceEngineService._call_groq(prompt)
            elif settings.GEMINI_API_KEY:
                raw_json_response = EvidenceEngineService._call_gemini(prompt)
            else:
                # If neither key exists, we safely fallback to "Unknown"
                return DomainClassification(current_domains=["Unknown"], target_domains=["Unknown"])
                
            # Convert the raw JSON string from the AI into a Python dictionary
            parsed_data = json.loads(raw_json_response)
            
            # **parsed_data unpacks the dictionary directly into the Pydantic schema
            return DomainClassification(**parsed_data)
            
        except Exception:
            # If the AI hallucinates bad JSON or the network fails, we don't crash the app.
            return DomainClassification(current_domains=["Unknown"], target_domains=prefs.preferred_roles)

    @staticmethod
    def _call_groq(prompt: str) -> str:
        """
        Sends the prompt to the Groq API.
        """
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }
        # urllib is Python's built-in tool for making HTTP requests (like sending data over the internet).
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as response:
            res = json.loads(response.read().decode("utf-8"))
            return res["choices"][0]["message"]["content"]

    @staticmethod
    def _call_gemini(prompt: str) -> str:
        """
        Sends the prompt to the Google Gemini API.
        """
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.1}
        }
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as response:
            res = json.loads(response.read().decode("utf-8"))
            return res["candidates"][0]["content"]["parts"][0]["text"]
