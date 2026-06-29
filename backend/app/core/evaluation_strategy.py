from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Set
from app.schemas.evidence import (
    EvidenceStatus, 
    EvidenceQuality, 
    KnowledgeItem,
    EvidenceReference
)
from app.core import evidence_config

class EvaluationStrategy(ABC):
    @abstractmethod
    def evaluate_knowledge(self, item: KnowledgeItem) -> Tuple[int, int, int, int, int, EvidenceQuality, EvidenceStatus, str]:
        """
        Evaluate a single knowledge item and return intermediate and final scores.
        Returns:
            (confidence_score, source_strength, evidence_diversity, practical_demonstration, academic_support, quality, status, reasoning)
        """
        pass

    @abstractmethod
    def generate_strengths_weaknesses(self, evaluations: dict) -> Tuple[List[str], List[str]]:
        """
        Generate overall strengths and weaknesses from all evaluations.
        """
        pass

class DefaultEvaluationStrategy(EvaluationStrategy):
    
    def evaluate_knowledge(self, item: KnowledgeItem) -> Tuple[int, int, int, int, int, EvidenceQuality, EvidenceStatus, str]:
        if not item.evidence:
            return 0, 0, 0, 0, 0, EvidenceQuality.LOW, EvidenceStatus.CLAIMED, "No evidence provided."
            
        sources_seen, source_strength_sum, practical, academic = self._analyze_evidence_list(item.evidence)
        
        diversity = self._compute_diversity(len(sources_seen))
        source_strength = self._compute_source_strength(source_strength_sum, len(item.evidence))
        
        practical = min(100, practical)
        academic = min(100, academic)
        
        confidence = self._compute_confidence(source_strength, diversity, practical, academic)
        
        quality, status = self._compute_status(confidence, practical, sources_seen)
        
        reasoning = self._build_reasoning(item)
            
        return (confidence, source_strength, diversity, practical, academic, quality, status, reasoning)

    def _analyze_evidence_list(self, evidence: List[EvidenceReference]) -> Tuple[Set[str], int, int, int]:
        sources_seen = set()
        source_strength_sum = 0
        practical = 0
        academic = 0
        
        for ref in evidence:
            source_type = ref.source_type
            sources_seen.add(source_type)
            
            weight = evidence_config.SOURCE_WEIGHTS.get(source_type, evidence_config.DEFAULT_SOURCE_WEIGHT)
            source_strength_sum += weight
            
            if source_type in ["EXPERIENCE", "PROJECT"]:
                practical += weight
            elif source_type in ["EDUCATION", "CERTIFICATION"]:
                academic += weight
                
        return sources_seen, source_strength_sum, practical, academic

    def _compute_diversity(self, num_sources: int) -> int:
        return evidence_config.DIVERSITY_RULES.get(num_sources, evidence_config.DEFAULT_DIVERSITY_SCORE)

    def _compute_source_strength(self, strength_sum: int, evidence_count: int) -> int:
        avg_strength = strength_sum / evidence_count
        bonus = min(evidence_config.SOURCE_STRENGTH_SCALING["MAX_BONUS"], evidence_count * evidence_config.SOURCE_STRENGTH_SCALING["BASE_MULTIPLIER"])
        return min(100, int(avg_strength + bonus))

    def _compute_confidence(self, source_strength: int, diversity: int, practical: int, academic: int) -> int:
        base_confidence = int(
            (source_strength * evidence_config.CONFIDENCE_SOURCE_WEIGHT) + 
            (diversity * evidence_config.CONFIDENCE_DIVERSITY_WEIGHT) + 
            (practical * evidence_config.CONFIDENCE_PRACTICAL_WEIGHT)
        )
        confidence = min(100, base_confidence)
        
        if practical == 0 and academic > 0:
            confidence = min(evidence_config.CONFIDENCE_CAPS["ACADEMIC_ONLY"], confidence)
        elif practical == 0 and academic == 0:
            confidence = min(evidence_config.CONFIDENCE_CAPS["CLAIMED_ONLY"], confidence)
            
        return confidence

    def _compute_status(self, confidence: int, practical: int, sources_seen: Set[str]) -> Tuple[EvidenceQuality, EvidenceStatus]:
        if confidence >= evidence_config.QUALITY_THRESHOLDS["HIGH"]:
            return EvidenceQuality.HIGH, EvidenceStatus.STRONGLY_DEMONSTRATED
            
        if confidence >= evidence_config.QUALITY_THRESHOLDS["MEDIUM"]:
            return EvidenceQuality.MEDIUM, EvidenceStatus.DEMONSTRATED
            
        if confidence >= evidence_config.QUALITY_THRESHOLDS["LOW"]:
            status = EvidenceStatus.PROFESSIONAL if practical > 0 else EvidenceStatus.ACADEMIC
            return EvidenceQuality.LOW, status
            
        status = EvidenceStatus.CLAIMED if (len(sources_seen) == 1 and "SKILL" in sources_seen) else EvidenceStatus.WEAK_EVIDENCE
        return EvidenceQuality.LOW, status

    def _build_reasoning(self, item: KnowledgeItem) -> str:
        reasoning_parts = []
        counts = {}
        for ref in item.evidence:
            counts[ref.source_type] = counts.get(ref.source_type, 0) + 1
            
        if counts.get("EXPERIENCE", 0) > 0:
            reasoning_parts.append(f"Demonstrated across {counts['EXPERIENCE']} professional roles.")
        if counts.get("PROJECT", 0) > 0:
            reasoning_parts.append(f"Applied in {counts['PROJECT']} practical projects.")
        if counts.get("EDUCATION", 0) > 0:
            reasoning_parts.append("Supported by academic coursework.")
        if counts.get("CERTIFICATION", 0) > 0:
            reasoning_parts.append("Validated by professional certification.")
        if counts.get("SKILL", 0) > 0 and len(counts) == 1:
            reasoning_parts.append("Appears only as a claimed skill with no supporting context.")
            
        reasoning = " ".join(reasoning_parts)
        return reasoning if reasoning else "Evidence evaluated."

    def generate_strengths_weaknesses(self, evaluations: dict) -> Tuple[List[str], List[str]]:
        strengths = []
        weaknesses = []
        
        high_conf = [name for name, e in evaluations.items() if e.confidence_score >= evidence_config.REPORTING_THRESHOLDS["HIGH_CONFIDENCE_MIN"]]
        med_conf = [name for name, e in evaluations.items() if evidence_config.REPORTING_THRESHOLDS["MEDIUM_CONFIDENCE_MIN"] <= e.confidence_score < evidence_config.REPORTING_THRESHOLDS["HIGH_CONFIDENCE_MIN"]]
        weak = [name for name, e in evaluations.items() if e.evidence_status in [EvidenceStatus.CLAIMED, EvidenceStatus.WEAK_EVIDENCE]]
        
        if len(high_conf) >= evidence_config.REPORTING_THRESHOLDS["STRONG_AREAS_MIN_COUNT"]:
            strengths.append(f"Strongly demonstrated expertise in {len(high_conf)} key areas, including {', '.join(high_conf[:2])}.")
        elif len(high_conf) > 0:
            strengths.append(f"Proven practical experience with {', '.join(high_conf)}.")
            
        practical_items = [name for name, e in evaluations.items() if e.practical_demonstration > 0]
        if len(practical_items) >= evidence_config.REPORTING_THRESHOLDS["PRACTICAL_AREAS_MIN_COUNT"]:
            strengths.append("Consistent track record of applying technologies in professional or project environments.")
            
        if len(weak) >= evidence_config.REPORTING_THRESHOLDS["WEAK_CLAIMS_MIN_COUNT"]:
            weaknesses.append(f"Several technologies are claimed without supporting evidence, such as {', '.join(weak[:2])}.")
        elif len(weak) > 0:
            weaknesses.append(f"Minimal practical evidence found for {', '.join(weak)}.")
            
        academic_only = [name for name, e in evaluations.items() if e.academic_support > 0 and e.practical_demonstration == 0]
        if len(academic_only) >= evidence_config.REPORTING_THRESHOLDS["ACADEMIC_ONLY_MIN_COUNT"]:
            weaknesses.append(f"Skills like {', '.join(academic_only[:2])} appear only in academic contexts without practical application.")
            
        if not strengths:
            strengths.append("Candidate demonstrates a baseline level of claimed skills.")
        if not weaknesses:
            weaknesses.append("No significant gaps or inconsistencies identified in the candidate's core profile.")
            
        return strengths[:3], weaknesses[:3]
