import logging
from typing import Dict
from app.schemas.evidence import (
    UnifiedKnowledge,
    CandidateEvidenceReport,
    KnowledgeEvaluation
)
from app.core.evaluation_strategy import EvaluationStrategy

logger = logging.getLogger(__name__)

class EvidenceEngineV2:
    """
    Evidence Engine V2: The Candidate Reasoning Engine.
    
    This service operates purely in the Reasoning Phase. It does not parse resumes
    or extract new knowledge. It evaluates the credibility, quality, and confidence
    of existing CandidateKnowledge using a provided EvaluationStrategy.
    """

    @staticmethod
    def evaluate(unified_knowledge: UnifiedKnowledge, strategy: EvaluationStrategy) -> CandidateEvidenceReport:
        logger.info("EvidenceEngineV2: Starting candidate reasoning phase.")
        
        evaluations: Dict[str, KnowledgeEvaluation] = {}
        
        # 1. Evaluate Technologies
        for tech in unified_knowledge.technologies:
            conf, src_str, div, prac, acad, qual, status, reasoning = strategy.evaluate_knowledge(tech)
            
            evaluations[tech.name] = KnowledgeEvaluation(
                name=tech.name,
                category="TECHNOLOGY",
                confidence_score=conf,
                source_strength=src_str,
                evidence_diversity=div,
                practical_demonstration=prac,
                academic_support=acad,
                evidence_quality=qual,
                evidence_status=status,
                reasoning=reasoning
            )
            
        # 2. Evaluate Capabilities
        for cap in unified_knowledge.capabilities:
            conf, src_str, div, prac, acad, qual, status, reasoning = strategy.evaluate_knowledge(cap)
            
            evaluations[cap.name] = KnowledgeEvaluation(
                name=cap.name,
                category="CAPABILITY",
                confidence_score=conf,
                source_strength=src_str,
                evidence_diversity=div,
                practical_demonstration=prac,
                academic_support=acad,
                evidence_quality=qual,
                evidence_status=status,
                reasoning=reasoning
            )
            
        # 3. Generate Strengths & Weaknesses deterministically
        strengths, weaknesses = strategy.generate_strengths_weaknesses(evaluations)
        
        logger.info(f"EvidenceEngineV2: Evaluated {len(evaluations)} knowledge items.")
        
        # 4. Construct Final Report
        return CandidateEvidenceReport(
            evaluations=evaluations,
            overall_strengths=strengths,
            overall_weaknesses=weaknesses
        )
