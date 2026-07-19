import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from app.core.llm_factory import get_llm


from app.core.config import settings
from app.graph.state import IntelligenceGraphState
from app.graph.schemas.market_intelligence import (
    RecommendationResult, GapAnalysis, Recommendation, RecommendationLevel, SkillMatchStatus
)


def _build_candidate_project_context(evidence) -> str:
    """
    Extracts rich project context from candidate evidence including
    project titles AND the technologies they used in each project.
    """
    # Build a mapping: project_title -> set of technologies used
    project_tech_map: Dict[str, set] = {}

    if evidence and evidence.skill_evidence:
        for skill_name, item in evidence.skill_evidence.items():
            for src in item.sources:
                if src.startswith("project:"):
                    project_title = src.replace("project:", "").strip()
                    if project_title not in project_tech_map:
                        project_tech_map[project_title] = set()
                    project_tech_map[project_title].add(skill_name)

    if not project_tech_map:
        return "None listed"

    # Format: "ProjectTitle (tech1, tech2, tech3)"
    lines = []
    for title, techs in project_tech_map.items():
        if techs:
            lines.append(f"- {title} ({', '.join(sorted(techs))})")
        else:
            lines.append(f"- {title}")

    return "\n".join(lines)


def _build_fallback_recommendations(
    priority_gaps: List[str],
    weak_evidence: List[str],
    role: str,
    candidate_level: str,
    core_responsibilities: List[str]
) -> List[Recommendation]:
    """
    Generates deterministic fallback recommendations when all LLMs fail.
    More targeted than a generic placeholder — uses priority gaps and
    weak evidence to produce at least semi-useful suggestions.
    """
    recs = []

    # Target priority gaps first
    for gap in priority_gaps[:3]:
        recs.append(Recommendation(
            title=f"Build a Project Using {gap}",
            reason=f"{gap} is a high-priority gap for {role} roles in 2026 hiring.",
            action=(
                f"Create a small end-to-end project that integrates {gap} as a core component. "
                f"Deploy it publicly and document the architecture in a README."
                if candidate_level in ("Fresher", "Junior")
                else
                f"Design and implement a production-grade feature using {gap}, covering scalability, "
                f"error handling, and observability. Write an architecture decision record (ADR)."
            ),
            impact=RecommendationLevel.HIGH,
            effort=RecommendationLevel.MEDIUM
        ))

    # Address weak evidence (claimed but unproven) if space remains
    for skill in weak_evidence[:2]:
        if len(recs) >= 5:
            break
        recs.append(Recommendation(
            title=f"Prove {skill} Proficiency With Evidence",
            reason=f"{skill} appears in your profile but lacks verifiable project evidence — recruiters discount unproven claims.",
            action=(
                f"Add {skill} to an existing project or build a new one specifically showcasing it. "
                f"Push the code to GitHub with a clear README."
            ),
            impact=RecommendationLevel.MEDIUM,
            effort=RecommendationLevel.LOW
        ))

    if not recs:
        recs.append(Recommendation(
            title="Build a Full-Stack Portfolio Project",
            reason=f"No strong technical evidence was found for core {role} technologies.",
            action="Build and deploy a complete API + database application using the most in-demand stack for your target role.",
            impact=RecommendationLevel.HIGH,
            effort=RecommendationLevel.MEDIUM
        ))

    return recs[:5]


class RecommendationAgentNode:
    """
    Node 2 in the Candidate Career Intelligence LangGraph.
    Generates level-aware and role-relevant career coaching advice and portfolio projects.
    Consumes evidence and market research findings to create actionable next steps.
    """

    @staticmethod
    async def run(state: IntelligenceGraphState) -> Dict[str, Any]:
        evidence = state.get("evidence")
        market_intel_map = state.get("market_intelligence")

        if not evidence or not market_intel_map:
            raise ValueError("Required inputs (evidence or market_intelligence) are missing from the state.")

        candidate_level = evidence.candidate_level.title

        # Build rich project context including tech stack used in each project
        candidate_projects_text = _build_candidate_project_context(evidence)

        # Build domain context from evidence
        current_domains = ", ".join(evidence.current_domains) if evidence.current_domains else "Not specified"
        target_domains = ", ".join(evidence.target_domains) if evidence.target_domains else "Not specified"

        recommendations_map = {}

        # Process each target role individually
        for role, intel in market_intel_map.items():

            # --- PHASE 1: Deterministic Gap Analysis ---
            strengths = []
            weak_evidence = []
            missing_skills = []

            all_segmented_skills = []
            for s in intel.must_have_skills:
                all_segmented_skills.append((s, "must_have"))
            for s in intel.strong_advantage_skills:
                all_segmented_skills.append((s, "strong_advantage"))
            for s in intel.emerging_skills:
                all_segmented_skills.append((s, "emerging"))
            for s in intel.common_tools:
                all_segmented_skills.append((s, "common_tools"))

            # Categorize by pre-calculated match status from Node 1
            for s, cat in all_segmented_skills:
                match_status = s.match_status
                if match_status == SkillMatchStatus.DEMONSTRATED:
                    strengths.append(s.name)
                elif match_status == SkillMatchStatus.CLAIMED:
                    weak_evidence.append(s.name)
                elif match_status == SkillMatchStatus.MISSING or match_status is None:
                    missing_skills.append(s.name)

            # --- PHASE 2: Priority Gap Calculation ---
            demand_weights = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
            category_weights = {
                "must_have": 4,
                "strong_advantage": 3,
                "emerging": 2,
                "common_tools": 1
            }

            missing_with_scores = []
            for s, cat in all_segmented_skills:
                if s.name in missing_skills:
                    signal_str = s.demand_signal.value.upper() if hasattr(s.demand_signal, 'value') else str(s.demand_signal).upper()
                    sig_w = demand_weights.get(signal_str, 1)
                    cat_w = category_weights[cat]
                    rank_v = s.rank or 5
                    # Higher signal + higher category weight + lower rank number = higher score
                    score = (sig_w * 100) + (cat_w * 10) + (6 - rank_v)
                    missing_with_scores.append((s.name, score))

            missing_with_scores.sort(key=lambda item: item[1], reverse=True)
            priority_gaps = [name for name, score in missing_with_scores[:5]]

            # Build deterministic GapAnalysis
            gap_analysis_model = GapAnalysis(
                strengths=strengths,
                weak_evidence=weak_evidence,
                missing_skills=missing_skills,
                priority_gaps=priority_gaps
            )

            # Pull core responsibilities from Node 1
            core_responsibilities = intel.core_responsibilities or []
            responsibilities_text = (
                "\n".join(f"  - {r}" for r in core_responsibilities[:5])
                if core_responsibilities
                else "  - Not specified"
            )

            # --- PHASE 3: LLM Recommendation Generation ---
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a senior engineering career coach and technical hiring manager.
Your role is to generate 3 to 5 HIGHLY SPECIFIC, level-appropriate, high-ROI portfolio project recommendations.

CRITICAL RULES:
1. LEVEL-AWARENESS — "{candidate_level}" determines scope:
   - Fresher/Junior: Small-scale CRUD apps, basic REST APIs, simple cloud deploys, beginner ML pipelines.
   - Mid-Level: System design, caching layers, CI/CD, message queues, database optimization.
   - Senior: Distributed systems, observability, infra-as-code, microservice orchestration.

2. TECHNICAL SPECIFICITY — Name exact technologies. Never say "learn X framework" or "improve SQL skills".
   Say "Build a FastAPI service backed by PostgreSQL using SQLAlchemy ORM and deploy on Railway."

3. GAP-TARGETING — Recommendations MUST target "Priority Gaps" first. Each recommendation should
   clearly explain WHICH gap it closes and WHY that matters for the target role.

4. WEAK EVIDENCE ACTION — For "Claimed (Lacking Evidence)" skills, recommend a specific project or
   contribution that PROVES the skill exists in a GitHub repository. Recruiters ignore unproven claims.

5. BUILD ON EXISTING PROJECTS — Where possible, suggest extending existing projects instead of
   starting new ones from scratch. Reference the candidate's actual listed projects.

6. NO SOFT SKILLS — Never recommend: communication, leadership, teamwork, Git basics, or generic
   "software engineering" improvements.

7. NO FILLER — Avoid motivational phrases. Be direct and precise.

You MUST return a JSON object matching the RecommendationResult schema exactly.
"""),
                ("user", """
CANDIDATE PROFILE:
- Seniority Level: {candidate_level}
- Current Technical Domain: {current_domains}
- Target Role Domain: {target_domains}

EXISTING PROJECTS (title: tech stack used):
{candidate_projects}

TARGET ROLE: "{role}"
ROLE RESPONSIBILITIES FROM MARKET RESEARCH:
{responsibilities}

DETERMINISTIC GAP ANALYSIS:
- Demonstrated Strengths: {strengths}
- Claimed But Unproven (weak evidence): {weak_evidence}
- Completely Missing From Profile: {missing_skills}
- TOP PRIORITY GAPS (address these first): {priority_gaps}

Generate 3 to 5 recommendations targeting priority gaps first, then weak evidence.
Each recommendation must name specific technologies, tools, and deployment targets.
""")
            ])

            payload_vars = {
                "candidate_level": candidate_level,
                "current_domains": current_domains,
                "target_domains": target_domains,
                "candidate_projects": candidate_projects_text,
                "role": role,
                "responsibilities": responsibilities_text,
                "strengths": ", ".join(strengths) if strengths else "None identified",
                "weak_evidence": ", ".join(weak_evidence) if weak_evidence else "None",
                "missing_skills": ", ".join(missing_skills) if missing_skills else "None",
                "priority_gaps": ", ".join(priority_gaps) if priority_gaps else "None"
            }

            llm_result = None

            provider = getattr(settings, "LLM_PROVIDER", "gemini")
            if provider in ("groq", "grok"):
                try:
                    llm = get_llm(
                        provider="groq",
                        model="llama-3.3-70b-versatile",
                        temperature=0.2
                    )
                    structured_llm = llm.with_structured_output(RecommendationResult)
                    chain = prompt | structured_llm
                    llm_result = await chain.ainvoke(payload_vars)
                    print(f"[Recommendation Agent] Groq generation successful for {role}.")
                except Exception as e:
                    print(f"[Recommendation Agent] Groq generation failed for {role}: {e}")
            else:
                if settings.GEMINI_API_KEY:
                    try:
                        llm = get_llm(
                            provider="gemini",
                            model="gemini-2.5-flash",
                            temperature=0.2
                        )
                        structured_llm = llm.with_structured_output(RecommendationResult)
                        chain = prompt | structured_llm
                        llm_result = await chain.ainvoke(payload_vars)
                        print(f"[Recommendation Agent] Gemini generation successful for {role}.")
                    except Exception as e:
                        print(f"[Recommendation Agent] Gemini generation failed for {role}: {e}. Trying Groq...")

                if not llm_result and settings.GROQ_API_KEY:
                    try:
                        llm = get_llm(
                            provider="groq",
                            model="llama-3.3-70b-versatile",  # 70b for better structured output
                            temperature=0.2
                        )
                        structured_llm = llm.with_structured_output(RecommendationResult)
                        chain = prompt | structured_llm
                        llm_result = await chain.ainvoke(payload_vars)
                        print(f"[Recommendation Agent] Groq generation successful for {role}.")
                    except Exception as e:
                        print(f"[Recommendation Agent] Groq generation failed for {role}: {e}")


            # Deterministic fallback if both LLMs fail
            if not llm_result:
                print(f"[Recommendation Agent] Critical: All LLMs failed for {role}. Using deterministic fallback.")
                fallback_recs = _build_fallback_recommendations(
                    priority_gaps=priority_gaps,
                    weak_evidence=weak_evidence,
                    role=role,
                    candidate_level=candidate_level,
                    core_responsibilities=core_responsibilities
                )
                llm_result = RecommendationResult(
                    gap_analysis=gap_analysis_model,
                    recommendations=fallback_recs
                )
            else:
                # Always override gap_analysis with deterministic Phase 1/2 result
                # to guarantee correctness regardless of LLM output
                llm_result.gap_analysis = gap_analysis_model

            recommendations_map[role] = llm_result

        return {
            "recommendations": recommendations_map,
            "recommendations_generated_at": datetime.now(timezone.utc)
        }
