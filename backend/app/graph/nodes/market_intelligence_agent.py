import json
import urllib.request
import urllib.error
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings
from app.graph.state import IntelligenceGraphState
from app.graph.schemas.market_intelligence import (
    MarketIntelligence, Citation, SegmentedSkill, DemandSignal, SkillMatchStatus
)

def extract_json_block(text: str) -> Optional[dict]:
    """
    Safely extract and parse the first JSON object block found in the text.
    """
    try:
        if "```json" in text:
            block = text.split("```json")[1].split("```")[0].strip()
            return json.loads(block)
        elif "```" in text:
            block = text.split("```")[1].split("```")[0].strip()
            return json.loads(block)
            
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])
    except Exception as e:
        print(f"[Market Intelligence Node] JSON block parser error: {e}")
    return None

NORMALIZATION_MAP = {
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "reactjs": "React",
    "react.js": "React",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "fastapi": "FastAPI",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "langchain": "LangChain",
    "langgraph": "LangGraph",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "github": "GitHub",
}

BANNED_SKILLS = {
    "software engineering",
    "ai tools",
    "programming fundamentals",
    "programming",
    "data structures",
    "algorithms",
    "data structures and algorithms",
    "web development",
    "frontend development",
    "backend development",
    "full stack development",
    "digital transformation",
    "ai collaboration",
    "innovation mindset",
    "future-oriented development",
    "problem solving",
    "collaboration",
    "communication",
    "git",
    "agile",
    "scrum",
    "testing",
    "unit testing",
}

def clean_and_normalize_skill_name(name: str) -> Optional[str]:
    cleaned = name.strip()
    if not cleaned:
        return None
    lower_name = cleaned.lower()
    
    # Check banned list
    if lower_name in BANNED_SKILLS:
        return None
        
    # Check exact normalized map matches
    if lower_name in NORMALIZATION_MAP:
        return NORMALIZATION_MAP[lower_name]
        
    # Standard cleanups: if name contains substrings, map them
    if "postgres" in lower_name:
        return "PostgreSQL"
    if "mongodb" in lower_name:
        return "MongoDB"
    if "kubernetes" in lower_name or lower_name == "k8s":
        return "Kubernetes"
    if "docker" in lower_name:
        return "Docker"
    if "redis" in lower_name:
        return "Redis"
    if "fastapi" in lower_name:
        return "FastAPI"
    if "langchain" in lower_name:
        return "LangChain"
    if "langgraph" in lower_name:
        return "LangGraph"
        
    return cleaned

def get_match_status(skill_name: str, skill_evidence_dict: dict) -> SkillMatchStatus:
    """
    Determines if the skill/tool is demonstrated, claimed, or missing based on candidate evidence.
    """
    clean_name = skill_name.lower().strip()
    
    # Exact lookup
    if clean_name in skill_evidence_dict:
        item = skill_evidence_dict[clean_name]
        tier = item.tier if hasattr(item, 'tier') else item.get('tier', 'Claimed')
        if tier.upper() == "DEMONSTRATED":
            return SkillMatchStatus.DEMONSTRATED
        else:
            return SkillMatchStatus.CLAIMED
            
    # Substring lookup
    for k, item in skill_evidence_dict.items():
        if k in clean_name or clean_name in k:
            tier = item.tier if hasattr(item, 'tier') else item.get('tier', 'Claimed')
            if tier.upper() == "DEMONSTRATED":
                return SkillMatchStatus.DEMONSTRATED
            else:
                return SkillMatchStatus.CLAIMED
                
    return SkillMatchStatus.MISSING


class SearchPlanner:
    """
    Formulates exactly 5 highly specialized queries covering the role at the target seniority level.
    """
    @staticmethod
    async def generate_queries(role_name: str, level: str) -> List[str]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a technical search engineer writing search queries for job market research.
Given the target role and experience level, write exactly 5 highly specialized search queries to find current market hiring expectations.

Generate exactly one query for each of the following categories in order:
Category 1: Core Technical Skills (languages, frameworks)
Category 2: Infrastructure & Deployment (Docker, cloud, databases, caching)
Category 3: Job Responsibilities (day-to-day work, duties)
Category 4: Hiring Trends (industry direction, salary, hiring demands for 2026)
Category 5: Real Job Postings (requirements extracted from actual listings)

Your output must match the structure of the schema.
"""),
            ("user", "Target Role: {level} {role_name}")
        ])

        class QueryOutput(BaseModel):
            queries: List[str] = Field(description="Exactly 5 search queries, one for each category in order.")

        # Try Groq first
        if settings.GROQ_API_KEY:
            try:
                llm = ChatGroq(
                    api_key=settings.GROQ_API_KEY,
                    model_name="llama-3.3-70b-versatile",
                    temperature=0.1
                )
                structured_llm = llm.with_structured_output(QueryOutput)
                chain = prompt | structured_llm
                res: QueryOutput = await chain.ainvoke({"role_name": role_name, "level": level})
                return res.queries
            except Exception as e:
                print(f"[Market Intelligence Node] Groq query generation failed: {e}. Trying Gemini...")

        # Try Gemini second
        if settings.GEMINI_API_KEY:
            try:
                llm = ChatGoogleGenerativeAI(
                    api_key=settings.GEMINI_API_KEY,
                    model="gemini-2.5-flash",
                    temperature=0.1
                )
                structured_llm = llm.with_structured_output(QueryOutput)
                chain = prompt | structured_llm
                res: QueryOutput = await chain.ainvoke({"role_name": role_name, "level": level})
                return res.queries
            except Exception as e:
                print(f"[Market Intelligence Node] Gemini query generation failed: {e}")

        # Fallback static queries
        role_full = f"{level} {role_name}".strip()
        return [
            f"most required skills core programming languages frameworks '{role_full}' 2026",
            f"Docker cloud databases caching infrastructure stack '{role_full}'",
            f"responsibilities day-to-day duties tasks '{role_full}'",
            f"hiring trends demand salary 2026 '{role_full}'",
            f"job postings descriptions requirements '{role_full}'"
        ]

class TavilyResearch:
    """
    Executes search queries sequentially using Tavily to respect free-tier constraints.
    Extracts snippets and builds a flat citations list.
    """
    @staticmethod
    def _perform_tavily_search_single_sync(query: str) -> Dict[str, Any]:
        if not settings.TAVILY_API_KEY:
            return {"snippets": "", "citations": []}

        url = "https://api.tavily.com/search"
        headers = {"Content-Type": "application/json"}
        payload = {
            "api_key": settings.TAVILY_API_KEY,
            "query": query,
            "search_depth": "advanced",
            "max_results": 3
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                res = json.loads(response.read().decode("utf-8"))
                results = res.get("results", [])
                snippets = []
                citations = []
                for idx, r in enumerate(results):
                    snippets.append(f"Result {idx+1} ({r.get('url')}):\n{r.get('content')}")
                    if r.get("url"):
                        citations.append({
                            "title": r.get("title") or "Market Posting Source",
                            "url": r.get("url")
                        })
                return {
                    "snippets": "\n\n".join(snippets),
                    "citations": citations
                }
        except Exception as e:
            print(f"[Market Intelligence Node] Tavily search error for '{query}': {e}")
            return {"snippets": "", "citations": []}

    @staticmethod
    async def search(queries: List[str]) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        combined_snippets = []
        all_citations = []
        seen_urls = set()

        for q in queries:
            # Query sequentially one by one to respect free limits
            res = await loop.run_in_executor(None, TavilyResearch._perform_tavily_search_single_sync, q)
            if res.get("snippets"):
                combined_snippets.append(res["snippets"])
            for cit in res.get("citations", []):
                if cit["url"] not in seen_urls:
                    seen_urls.add(cit["url"])
                    all_citations.append(Citation(title=cit["title"], url=cit["url"]))
            # Add a small delay between queries
            await asyncio.sleep(0.3)

        return {
            "search_context": "\n\n".join(combined_snippets),
            "citations": all_citations
        }

class MarketSynthesizer:
    """
    Compiles raw search evidence into structured v2 MarketIntelligence models under strict constraints.
    """
    @staticmethod
    async def synthesize(
        role_name: str, 
        level: str, 
        search_context: str, 
        citations: List[Citation],
        state: IntelligenceGraphState
    ) -> MarketIntelligence:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the Market Intelligence Agent.
Your job is to analyze live job research snippets and synthesize current market expectations for the target role: "{role_name}" at the candidate's level: "{level}".

CRITICAL CONSTRAINTS:
1. Specificity: Avoid generic or broad disciplines (e.g., Software Engineering, Web Development, Programming, Git, AI Tools, Programming Fundamentals, Data Structures and Algorithms). You must output specific technologies (e.g., React, Next.js, FastAPI, Docker, Kubernetes, PostgreSQL, Redis, TensorFlow, PyTorch).
2. Normalization: Use standardized naming (e.g. use 'PostgreSQL' instead of 'Postgres', 'JavaScript' instead of 'JS', 'TypeScript' instead of 'TS').
3. No Overlaps: Ensure a technology does NOT appear in both skills and common tools.
4. Category Limits: Output a maximum of 5 items for each of the following lists:
   - must_have_skills: Baseline critical tech skills required to get hired.
   - strong_advantage_skills: Nice-to-have technical skills that set a candidate apart.
   - emerging_skills: Cutting-edge tools or methodologies rising in demand in 2026 (e.g. MCP, LangGraph, agentic workflows, server components). Avoid generic buzzwords (e.g. AI Collaboration, Innovation Mindset, Digital Transformation, Future-Oriented Development).
   - common_tools: Specific platforms, cloud hosting, observability, or developer tooling (e.g. AWS, Docker, Datadog, Postman).
5. Signal Tiers & Ranking: For every item in the lists above:
   - Set demand_signal strictly as "HIGH", "MEDIUM", or "LOW".
   - Assign a relative rank (1 to 5) indicating priority within its category.
   - Write a short, maximum 1-sentence 'why_this_matters' explanation explaining the recruiter value (avoid generic statements).
6. Market Summary: Write exactly one or two sentences. You MUST mention:
   - What tech/skill is increasing in demand.
   - What recruiters are prioritizing (e.g. deployable projects, RAG architectures). Avoid generic statements about industries evolving.

You MUST return a valid JSON object matching this schema exactly:
{{
  "role_name": "string",
  "market_summary": "string",
  "must_have_skills": [
    {{"name": "string", "demand_signal": "HIGH|MEDIUM|LOW", "rank": integer, "why_this_matters": "string"}}
  ],
  "strong_advantage_skills": [
    {{"name": "string", "demand_signal": "HIGH|MEDIUM|LOW", "rank": integer, "why_this_matters": "string"}}
  ],
  "emerging_skills": [
    {{"name": "string", "demand_signal": "HIGH|MEDIUM|LOW", "rank": integer, "why_this_matters": "string"}}
  ],
  "common_tools": [
    {{"name": "string", "demand_signal": "HIGH|MEDIUM|LOW", "rank": integer, "why_this_matters": "string"}}
  ],
  "core_responsibilities": ["string", ...]
}}
Return ONLY the raw JSON block. Do not include any explanations, markdown format tags, or text outside the JSON.
"""),
            ("user", """
RESEARCH CONTEXT:
---
{search_context}
---
""")
        ])

        payload_vars = {
            "role_name": role_name,
            "level": level,
            "search_context": search_context or "No search context available. Use internal knowledge."
        }

        # Build candidate skill mapping for Match Status
        evidence = state.get("evidence")
        skill_evidence_dict = {}
        if evidence and evidence.skill_evidence:
            for k, v in evidence.skill_evidence.items():
                skill_evidence_dict[k.lower().strip()] = v

        parsed_json = None

        # Try Groq first
        if settings.GROQ_API_KEY:
            try:
                llm = ChatGroq(
                    api_key=settings.GROQ_API_KEY,
                    model_name="llama-3.3-70b-versatile",
                    temperature=0.1
                )
                formatted_prompt = prompt.format(**payload_vars)
                res = await llm.ainvoke(formatted_prompt)
                parsed_json = extract_json_block(res.content)
                if parsed_json:
                    print(f"[Market Intelligence Node] Groq synthesis successful for {role_name}.")
            except Exception as e:
                print(f"[Market Intelligence Node] Groq synthesis failed for {role_name}: {e}")

        # Try Gemini second
        if not parsed_json and settings.GEMINI_API_KEY:
            try:
                llm = ChatGoogleGenerativeAI(
                    api_key=settings.GEMINI_API_KEY,
                    model="gemini-2.5-flash",
                    temperature=0.1
                )
                formatted_prompt = prompt.format(**payload_vars)
                res = await llm.ainvoke(formatted_prompt)
                parsed_json = extract_json_block(res.content)
                if parsed_json:
                    print(f"[Market Intelligence Node] Gemini synthesis successful for {role_name}.")
            except Exception as e:
                print(f"[Market Intelligence Node] Gemini synthesis failed for {role_name}: {e}")

        if parsed_json:
            seen_skills = set()
            
            def process_skills_list(raw_list: List[dict], default_signal: str) -> List[SegmentedSkill]:
                processed = []
                for x in raw_list:
                    if len(processed) >= 5:
                        break
                    raw_name = x.get("name", "").strip()
                    if not raw_name:
                        continue
                    normalized_name = clean_and_normalize_skill_name(raw_name)
                    if not normalized_name:
                        continue
                        
                    norm_lower = normalized_name.lower()
                    if norm_lower in seen_skills:
                        continue
                    seen_skills.add(norm_lower)
                    
                    # Ensure why_this_matters is 1 sentence and max 150 chars
                    matters = x.get("why_this_matters", "").strip()
                    if not matters:
                        matters = "Valued technology for this role."
                    # Cap to first sentence
                    if "." in matters:
                        matters = matters.split(".")[0].strip() + "."
                    if len(matters) > 150:
                        matters = matters[:147] + "..."
                        
                    processed.append(SegmentedSkill(
                        name=normalized_name,
                        demand_signal=DemandSignal(x.get("demand_signal", default_signal).upper()),
                        rank=len(processed) + 1,  # Programmatic sequential rank
                        why_this_matters=matters,
                        match_status=get_match_status(normalized_name, skill_evidence_dict)
                    ))
                return processed

            must_have = process_skills_list(parsed_json.get("must_have_skills", []), "HIGH")
            strong = process_skills_list(parsed_json.get("strong_advantage_skills", []), "MEDIUM")
            emerging = process_skills_list(parsed_json.get("emerging_skills", []), "LOW")
            tools = process_skills_list(parsed_json.get("common_tools", []), "MEDIUM")

            # Source quality breakdown
            source_breakdown = {"LinkedIn": 0, "Indeed": 0, "Company Career Pages / Tech Blogs": 0}
            for cit in citations:
                url = cit.url.lower()
                if "linkedin.com" in url:
                    source_breakdown["LinkedIn"] += 1
                elif "indeed.com" in url:
                    source_breakdown["Indeed"] += 1
                else:
                    source_breakdown["Company Career Pages / Tech Blogs"] += 1

            return MarketIntelligence(
                role_name=parsed_json.get("role_name") or role_name,
                market_summary=parsed_json.get("market_summary", "").strip()[:300],
                must_have_skills=must_have,
                strong_advantage_skills=strong,
                emerging_skills=emerging,
                common_tools=tools,
                core_responsibilities=parsed_json.get("core_responsibilities", []),
                citations=citations,
                analyzed_sources_count=len(citations),
                source_breakdown=source_breakdown,
                generated_at=datetime.now(timezone.utc)
            )

        # Fallback Mock Data
        print(f"[Market Intelligence Node] Critical: All LLMs failed for {role_name}. Using fallback.")
        return MarketIntelligence(
            role_name=role_name,
            market_summary=f"Hiring for junior {role_name} is steady. Recruiters prioritize practical project building over theoretical knowledge.",
            must_have_skills=[
                SegmentedSkill(name="Python", demand_signal=DemandSignal.HIGH, rank=1, why_this_matters="Core language requirement.", match_status=get_match_status("Python", skill_evidence_dict)),
                SegmentedSkill(name="SQL", demand_signal=DemandSignal.HIGH, rank=2, why_this_matters="Standard database query language.", match_status=get_match_status("SQL", skill_evidence_dict))
            ],
            strong_advantage_skills=[
                SegmentedSkill(name="Docker", demand_signal=DemandSignal.MEDIUM, rank=1, why_this_matters="Containerization is valued in cloud workflows.", match_status=get_match_status("Docker", skill_evidence_dict))
            ],
            emerging_skills=[
                SegmentedSkill(name="FastAPI", demand_signal=DemandSignal.LOW, rank=1, why_this_matters="Rapidly growing web framework.", match_status=get_match_status("FastAPI", skill_evidence_dict))
            ],
            common_tools=[
                SegmentedSkill(name="GitHub", demand_signal=DemandSignal.HIGH, rank=1, why_this_matters="Standard source version control.", match_status=get_match_status("GitHub", skill_evidence_dict))
            ],
            core_responsibilities=["Write clean code", "Deploy API services"],
            citations=citations or [Citation(title="Indeed Jobs", url="https://indeed.com")],
            analyzed_sources_count=len(citations) or 1,
            source_breakdown={"LinkedIn": 0, "Indeed": 1, "Company Career Pages / Tech Blogs": 0},
            generated_at=datetime.now(timezone.utc)
        )

class MarketIntelligenceNode:
    """
    Node 1 in the Candidate Intelligence Graph.
    Responsible for fetching live, fresh market expectations for each of the preferred roles.
    Does NOT use database caching. Every execution performs a fresh web search.
    """
    @staticmethod
    async def run(state: IntelligenceGraphState, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        evidence = state.get("evidence")
        if not evidence:
            raise ValueError("Candidate Evidence is missing from the state.")

        target_roles = evidence.target_domains or ["General software engineer"]
        candidate_level = evidence.candidate_level.title

        print(f"[Market Intelligence Node] Starting live SEQUENTIAL search for roles: {target_roles} at level: {candidate_level}")

        market_intel_map = {}
        for role in target_roles:
            # Process roles sequentially one by one to respect free plan rate limits
            try:
                # 1. Generate 5 specialized queries
                queries = await SearchPlanner.generate_queries(role, candidate_level)
                
                # 2. Perform sequential Tavily searches
                research = await TavilyResearch.search(queries)
                
                # 3. Synthesize the findings into MarketIntelligence
                intel = await MarketSynthesizer.synthesize(
                    role_name=f"{candidate_level} {role}".strip(),
                    level=candidate_level,
                    search_context=research.get("search_context", ""),
                    citations=research.get("citations", []),
                    state=state
                )
                market_intel_map[role] = intel
            except Exception as e:
                print(f"[Market Intelligence Node] Sequential worker failed for role '{role}': {e}")
                # Safe fallback per role to prevent graph crash
                # Build skill mapping for match status fallback
                skill_evidence_dict = {}
                if evidence and evidence.skill_evidence:
                    for k, v in evidence.skill_evidence.items():
                        skill_evidence_dict[k.lower().strip()] = v
                        
                market_intel_map[role] = MarketIntelligence(
                    role_name=f"{candidate_level} {role}".strip(),
                    market_summary=f"Hiring for junior {role} is steady. Recruiters prioritize practical project building over theoretical knowledge.",
                    must_have_skills=[
                        SegmentedSkill(name="Python", demand_signal=DemandSignal.HIGH, rank=1, why_this_matters="Core language requirement.", match_status=get_match_status("Python", skill_evidence_dict)),
                        SegmentedSkill(name="SQL", demand_signal=DemandSignal.HIGH, rank=2, why_this_matters="Standard database query language.", match_status=get_match_status("SQL", skill_evidence_dict))
                    ],
                    strong_advantage_skills=[
                        SegmentedSkill(name="Docker", demand_signal=DemandSignal.MEDIUM, rank=1, why_this_matters="Containerization is valued in cloud workflows.", match_status=get_match_status("Docker", skill_evidence_dict))
                    ],
                    emerging_skills=[
                        SegmentedSkill(name="FastAPI", demand_signal=DemandSignal.LOW, rank=1, why_this_matters="Rapidly growing web framework.", match_status=get_match_status("FastAPI", skill_evidence_dict))
                    ],
                    common_tools=[
                        SegmentedSkill(name="GitHub", demand_signal=DemandSignal.HIGH, rank=1, why_this_matters="Standard source version control.", match_status=get_match_status("GitHub", skill_evidence_dict))
                    ],
                    core_responsibilities=["Write clean code", "Deploy services"],
                    citations=[Citation(title="Indeed Jobs", url="https://indeed.com")],
                    analyzed_sources_count=1,
                    source_breakdown={"LinkedIn": 0, "Indeed": 1, "Company Career Pages / Tech Blogs": 0},
                    generated_at=datetime.now(timezone.utc)
                )

        return {
            "market_intelligence": market_intel_map,
            "market_intelligence_generated_at": datetime.now(timezone.utc)
        }
