import logging
import json
from typing import Dict, Any, List
from app.explanation.prompts.job_match_prompt import EXPLANATION_PROMPT

logger = logging.getLogger(__name__)

class PromptBuilder:
    @staticmethod
    def build_candidate_context(comparison_evidence: dict) -> str:
        """
        Extracts candidate identity info directly from MatchKnowledge context.
        """
        ctx = comparison_evidence.get("candidate_context", {})
        level = ctx.get("level", "Unknown")
        domain = ctx.get("primary_domain", "Unknown")
        exp = ctx.get("total_experience_months", 0)

        lines = [
            f"Level: {level}",
            f"Primary Domain: {domain}",
            f"Total Experience: {exp} months"
        ]
        return "\n".join(line for line in lines if line)

    @staticmethod
    def build_job_context(job_title: str, company_name: str, comparison_evidence: dict, index: int, job_id: str) -> str:
        """
        Formats a single job's comparison evidence into a serialized prompt block.
        """
        # Strip out the candidate context from the individual job blocks to save tokens
        evidence_copy = dict(comparison_evidence)
        if "candidate_context" in evidence_copy:
            del evidence_copy["candidate_context"]
            
        lines = [
            f"--- JOB {index + 1} ---",
            f"job_id: {job_id}",
            f"Title: {job_title}",
            f"Company: {company_name}",
            "MatchKnowledge JSON:",
            json.dumps(evidence_copy, indent=2)
        ]
        return "\n".join(lines)

    @staticmethod
    def build_batch_prompt(jobs: List[Dict[str, Any]]) -> str:
        """
        Builds the final prompt for a batch of jobs.
        Each entry in `jobs` is: {
            "job_title": str,
            "company_name": str,
            "comparison_evidence": dict,
            "job_search_result_id": str
        }
        """
        if not jobs:
            return ""
            
        # Extract candidate context from the first job's MatchKnowledge
        candidate_ctx = PromptBuilder.build_candidate_context(jobs[0]["comparison_evidence"])

        job_blocks = []
        for idx, entry in enumerate(jobs):
            job_title = entry["job_title"]
            company_name = entry["company_name"]
            evidence = entry["comparison_evidence"]
            job_id = entry["job_search_result_id"]
            job_blocks.append(PromptBuilder.build_job_context(job_title, company_name, evidence, idx, job_id))

        jobs_ctx = "\n\n".join(job_blocks)

        prompt = EXPLANATION_PROMPT.format(
            candidate_context=candidate_ctx,
            jobs_context=jobs_ctx
        )
        logger.info(f"[PromptBuilder] Built prompt for {len(jobs)} jobs without requiring raw CandidateKnowledge.")
        return prompt
