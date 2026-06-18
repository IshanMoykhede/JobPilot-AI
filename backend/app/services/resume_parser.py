import json
import urllib.request
import urllib.error
import re
from typing import Dict, Any, Optional
from app.core.config import settings
from app.schemas.candidate_profile import ResumeDataSchema

class ResumeParserService:
    @staticmethod
    def parse_resume_text(resume_text: str) -> ResumeDataSchema:
        """
        Parses raw resume text into structured Candidate Resume Schema using LLM (Groq Llama or Gemini).
        """
        if not settings.GROQ_API_KEY and not settings.GEMINI_API_KEY:
            raise ValueError("No AI API Keys configured. Please set GEMINI_API_KEY or GROQ_API_KEY in your backend .env file.")

        prompt = f"""You are a precise resume parser. Extract structured information from the following raw resume text.
You must return only a valid, raw JSON object matching the JSON schema below.
Do not output markdown format (like ```json), do not include backticks, do not include explanations, intro or outro text. Return only the raw JSON.

JSON Schema:
{{
  "contact_info": {{
    "phone": string or null,
    "linkedin_url": string (absolute URL starting with http/https, or null),
    "github_url": string (absolute URL starting with http/https, or null),
    "portfolio_url": string (absolute URL starting with http/https, or null)
  }},
  "summary": string or null,
  "skills": [string, ...],
  "experience": [
    {{
      "company": string,
      "role": string,
      "start_date": string or null (format: YYYY-MM or similar),
      "end_date": string or null (format: YYYY-MM or 'Present'),
      "description": string or null
    }}
  ],
  "education": [
    {{
      "institution": string,
      "degree": string,
      "year": string
    }}
  ],
  "projects": [
    {{
      "title": string,
      "description": string or null,
      "technologies": [string, ...]
    }}
  ],
  "certifications": [
    {{
      "name": string,
      "issuer": string or null,
      "year": string or null,
      "url": string or null
    }}
  ],
  "co_curricular_activities": [string, ...]
}}

Rules:
1. Extract ONLY information that is present in the resume text. Do not hallucinate or invent information.
2. If any field or array is missing in the text, return null or an empty array.
3. Make sure LinkedIn/GitHub/Portfolio URLs are absolute URLs (start with https:// or http://). If you extract 'github.com/user', return 'https://github.com/user'. If invalid or not a URL, return null.

Raw Resume Text:
{resume_text}
"""

        raw_json_response = None
        if settings.GROQ_API_KEY:
            raw_json_response = ResumeParserService._call_groq(prompt)
        elif settings.GEMINI_API_KEY:
            raw_json_response = ResumeParserService._call_gemini(prompt)

        if not raw_json_response:
            raise ValueError("Received empty response from LLM parser service.")

        # Parse JSON
        try:
            parsed_data = json.loads(raw_json_response)
        except json.JSONDecodeError:
            # Try cleaning response (sometimes LLMs return markdown code blocks anyway)
            cleaned = ResumeParserService._clean_json_string(raw_json_response)
            try:
                parsed_data = json.loads(cleaned)
            except json.JSONDecodeError:
                raise ValueError(f"Failed to parse LLM response as JSON. Raw response: {raw_json_response}")

        # Preprocess and clean URLs to satisfy Pydantic HttpUrl validation
        ResumeParserService._sanitize_urls(parsed_data)

        # Validate with Pydantic Schema
        try:
            validated_data = ResumeDataSchema(**parsed_data)
            return validated_data
        except Exception as e:
            raise ValueError(f"Pydantic schema validation failed: {str(e)}")

    @staticmethod
    def _call_groq(prompt: str) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                res = json.loads(response.read().decode("utf-8"))
                return res["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise ValueError(f"Groq API Error ({e.code}): {error_body}")
        except Exception as e:
            raise ValueError(f"Failed to connect to Groq API: {str(e)}")

    @staticmethod
    def _call_gemini(prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.1
            }
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                res = json.loads(response.read().decode("utf-8"))
                return res["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise ValueError(f"Gemini API Error ({e.code}): {error_body}")
        except Exception as e:
            raise ValueError(f"Failed to connect to Gemini API: {str(e)}")

    @staticmethod
    def _clean_json_string(text: str) -> str:
        text = re.sub(r"^```[a-zA-Z]*\n", "", text, flags=re.MULTILINE)
        text = re.sub(r"\n```$", "", text, flags=re.MULTILINE)
        return text.strip()

    @staticmethod
    def _sanitize_urls(data: Dict[str, Any]):
        contact = data.get("contact_info")
        if not contact or not isinstance(contact, dict):
            return
            
        url_fields = ["linkedin_url", "github_url", "portfolio_url"]
        for field in url_fields:
            val = contact.get(field)
            if val and isinstance(val, str):
                val = val.strip()
                if val.lower() in ["none", "null", ""]:
                    contact[field] = None
                    continue
                if not val.startswith("http://") and not val.startswith("https://"):
                    contact[field] = f"https://{val}"
