import logging
from app.preprocessing.normalization_pipeline import NormalizationPipeline
from app.compliance.compliance_engine import ComplianceEngine
from app.intelligence.semantic_similarity_engine import SemanticSimilarityEngine
from app.intelligence.lexical_similarity_engine import LexicalSimilarityEngine
from app.intelligence.phonetic_similarity_engine import PhoneticSimilarityEngine
from app.intelligence.tfidf_vector_engine import TFIDFVectorEngine
from app.intelligence.ngram_similarity_engine import NGramSimilarityEngine
from app.orchestration.decision_engine import DecisionEngine
from app.orchestration.probability_model import ProbabilityModel
from app.orchestration.explanation_builder import ExplanationBuilder
from app.orchestration.dynamic_scoring import DynamicScoringModule
from app.orchestration.confidence_scorer import ConfidenceScorer
from app.preprocessing.structural_pattern_detector import StructuralPatternDetector
from app.interpretability.bionic_conflict_highlighter import BionicConflictHighlighter
from app.monitoring.audit_logger import AuditLogger
from app.configuration.scoring_weights import SCORING_WEIGHTS
from app.api.request_models import ComplianceResult, ConflictDetail
from metaphone import doublemetaphone
from app.persistence.title_repository import TitleRepository

class MetrixaOrchestrator:
    def __init__(self):
        self.normalizer = NormalizationPipeline()
        self.compliance = ComplianceEngine()
        self.semantic = SemanticSimilarityEngine()
        self.lexical = LexicalSimilarityEngine()
        self.phonetic = PhoneticSimilarityEngine()
        self.tfidf = TFIDFVectorEngine()
        self.ngram = NGramSimilarityEngine()
        self.repo = TitleRepository()
        
        # Advanced Intelligence & Governance
        self.decision = DecisionEngine()
        self.probability = ProbabilityModel()
        self.explainer = ExplanationBuilder()
        self.highlighter = BionicConflictHighlighter()
        self.dynamic_scorer = DynamicScoringModule()
        self.confidence_scorer = ConfidenceScorer()
        self.pattern_detector = StructuralPatternDetector()
        self.audit_logger = AuditLogger()

    async def verify(self, title: str) -> ComplianceResult:
        # 1. Normalize
        normalized_query = self.normalizer.normalize(title)
        
        # 2. Fetch existing titles for combination detection
        existing_titles = await self.repo.get_all_titles()
        
        # 3. Compliance check (Deterministic + Combination)
        compliance_res = await self.compliance.check_compliance(title, existing_titles)
        
        # 4. Pattern Detection
        patterns = self.pattern_detector.detect_patterns(title)
        
        # 5. Candidate Retrieval (Using placeholder for demo)
        candidate_title = "Morning News"
        
        # 6. Compute Similarities (Dual-Pass for prefixes/periodicity)
        # Pass 1: Original Title
        sem_sim = await self.semantic.calculate_similarity(title, candidate_title)
        lex_sim = await self.lexical.calculate_similarity(title, candidate_title)
        pho_sim = await self.phonetic.calculate_similarity(title, candidate_title)
        
        # Pass 2: Base Titles (if cleaned titles exist from compliance layer)
        for cleaned in compliance_res.get("cleaned_titles", []):
            sem_c = await self.semantic.calculate_similarity(cleaned, candidate_title)
            lex_c = await self.lexical.calculate_similarity(cleaned, candidate_title)
            pho_c = await self.phonetic.calculate_similarity(cleaned, candidate_title)
            
            # Take max similarity to handle hidden overlaps (Phase 10)
            sem_sim = max(sem_sim, sem_c)
            lex_sim = max(lex_sim, lex_c)
            pho_sim = max(pho_sim, pho_c)
            
        initial_scores = {
            "semantic_similarity": sem_sim,
            "lexical_similarity": lex_sim,
            "phonetic_similarity": pho_sim
        }
        
        # 7. Lean 6 Dynamic Weighted Scoring
        weights = self.dynamic_scorer.adjust_weights(title, [candidate_title], initial_scores)
        final_sim = (
            sem_sim * weights.get("semantic_similarity", 0.6) +
            pho_sim * weights.get("phonetic_similarity", 0.25) +
            lex_sim * weights.get("lexical_similarity", 0.15)
        )
        
        # High Agreement Boost (Phase 10)
        final_sim = self.dynamic_scorer.apply_agreement_boost(final_sim, initial_scores)
        
        # 8. Compute Confidence & Decision
        # If compliance penalty found (e.g. Disallowed word or Combination), override similarity
        if not compliance_res["is_compliant"] and compliance_res["penalty_score"] >= 1.0:
            final_sim = 1.0
            
        confidence = self.confidence_scorer.calculate_confidence(initial_scores)
        prob = self.probability.compute_probability(final_sim)
        
        decision_meta = self.decision.categorize_decision(
            final_sim, compliance_res["is_compliant"], confidence
        )
        
        # 9. Collect Conflict Details & Highlights
        conflict_data = {
            "tokens": list(set(title.lower().split()) & set(candidate_title.lower().split())),
            "rules": compliance_res.get("violations_terms", []),
            "phonetic": [doublemetaphone(w)[0] for w in candidate_title.split()]
        }
        
        highlighted_input = self.highlighter.highlight(title, conflict_data)
        
        # 10. Build Explanation
        explanation = self.explainer.build_explanation(compliance_res, initial_scores, decision_meta["decision"])
        if patterns:
            explanation += f" | Structural patterns detected: {', '.join(patterns)}"
        
        result = ComplianceResult(
            is_compliant=compliance_res["is_compliant"] and decision_meta["decision"] != "Reject",
            verification_probability=prob,
            decision=decision_meta["decision"],
            explanation=explanation,
            conflicts=[
                ConflictDetail(
                    title=candidate_title,
                    conflict_type="Phase-10 Refined Similarity",
                    similarity_score=final_sim,
                    highlighted_text=highlighted_input
                )
            ],
            scores=initial_scores,
            metadata={
                "risk_tier": decision_meta["risk_tier"],
                "confidence_score": confidence,
                "structural_patterns": patterns
            }
        )
        
        # 11. Audit Logging
        self.audit_logger.log_verification(title, result.dict())
        
        return result
