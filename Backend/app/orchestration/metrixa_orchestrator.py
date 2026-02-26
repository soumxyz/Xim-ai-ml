import logging
import time
from app.preprocessing.normalization_pipeline import NormalizationPipeline
from app.compliance.compliance_engine import ComplianceEngine
from app.intelligence.semantic_similarity_engine import SemanticSimilarityEngine
from app.intelligence.lexical_similarity_engine import LexicalSimilarityEngine
from app.intelligence.phonetic_similarity_engine import PhoneticSimilarityEngine
from app.orchestration.decision_engine import DecisionEngine
from app.orchestration.probability_model import ProbabilityModel
from app.orchestration.explanation_builder import ExplanationBuilder
from app.orchestration.dynamic_scoring import DynamicScoringModule
from app.orchestration.confidence_scorer import ConfidenceScorer
from app.preprocessing.structural_pattern_detector import StructuralPatternDetector
from app.interpretability.bionic_conflict_highlighter import BionicConflictHighlighter
from app.monitoring.audit_logger import AuditLogger
from app.configuration.scoring_weights import SCORING_WEIGHTS
from app.api.request_models import ComplianceResult, ConflictDetail, AnalysisDetail
from app.persistence.title_repository import TitleRepository
from metaphone import doublemetaphone

class MetrixaOrchestrator:
    def __init__(self, ann_index=None, token_index=None, sbert_available=False):
        self.normalizer = NormalizationPipeline()
        self.compliance = ComplianceEngine()
        self.semantic = SemanticSimilarityEngine()
        self.lexical = LexicalSimilarityEngine()
        self.phonetic = PhoneticSimilarityEngine()
        self.repo = TitleRepository()
        
        # Shared in-memory indexes (injected from main.py)
        self.ann_index = ann_index
        self.token_index = token_index
        self.sbert_available = sbert_available
        
        # Intelligence & Governance
        self.decision = DecisionEngine()
        self.probability = ProbabilityModel()
        self.explainer = ExplanationBuilder()
        self.highlighter = BionicConflictHighlighter()
        self.dynamic_scorer = DynamicScoringModule()
        self.confidence_scorer = ConfidenceScorer()
        self.pattern_detector = StructuralPatternDetector()
        self.audit_logger = AuditLogger()
        self.logger = logging.getLogger("metrixa")

    async def verify(self, title: str) -> ComplianceResult:
        start_time = time.time()
        
        # 1. Normalize
        normalized_query = self.normalizer.normalize(title)
        
        # 2. Fetch existing titles for combination detection
        existing_titles = await self.repo.get_all_titles()
        
        # 3. Compliance check (Deterministic + Combination)
        compliance_res = await self.compliance.check_compliance(title, existing_titles)
        
        # 4. Pattern Detection
        patterns = self.pattern_detector.detect_patterns(title)
        
        # 5. Robust Candidate Retrieval via Token Index (Instant)
        candidates = []
        if self.token_index:
            query_tokens = normalized_query.split()
            candidates = await self.token_index.filter_by_tokens(query_tokens)
            self.logger.info(f"Token Index retrieved {len(candidates)} candidates.")
        
        # If no lexical candidates, return clean accept (or rejection if compliance failed)
        if not candidates:
            elapsed_ms = int((time.time() - start_time) * 1000)
            analysis_detail = AnalysisDetail(
                lexical_similarity=0,
                phonetic_similarity=0,
                semantic_similarity=0,
                disallowed_word=any(v in "; ".join(compliance_res["violations"]).lower() for v in ["disallowed", "restricted"]),
                periodicity_violation="periodicity" in "; ".join(compliance_res["violations"]).lower(),
                combination_violation="combination" in "; ".join(compliance_res["violations"]).lower(),
                prefix_suffix_violation="prefix" in "; ".join(compliance_res["violations"]).lower() or "suffix" in "; ".join(compliance_res["violations"]).lower()
            )
            return ComplianceResult(
                is_compliant=compliance_res["is_compliant"],
                verification_probability=100.0 if compliance_res["is_compliant"] else 0.0,
                decision="Reject" if not compliance_res["is_compliant"] else "Accept",
                explanation="No similar titles found." if compliance_res["is_compliant"] else "; ".join(compliance_res["violations"]),
                conflicts=[],
                scores={},
                analysis=analysis_detail,
                metadata={"risk_tier": "Low", "processing_time_ms": elapsed_ms, "candidates_checked": 0}
            )
        
        # 6. Deep Fuzzy Comparison on Candidates (using rapidfuzz)
        from rapidfuzz import fuzz
        best_match = None
        best_similarity = 0.0
        all_conflicts = []
        best_scores = {}
        
        # Score candidates using high-speed fuzzy matching
        for candidate in candidates[:50]:  # Check up to 50 candidates
            candidate_title = candidate.get("title", "")
            
            # Semantic search is disabled to prevent segfaults; using fuzzy as proxy
            sem_sim = 0.0 
            
            # High-performance lexical similarity via RapidFuzz
            lex_sim = fuzz.token_set_ratio(title, candidate_title) / 100.0
            lex_sim_simple = fuzz.ratio(title, candidate_title) / 100.0
            lex_sim = max(lex_sim, lex_sim_simple) # Take best of set vs ratio
            
            # Phonetic similarity fallback
            pho_sim = await self.phonetic.calculate_similarity(title, candidate_title)
            
            scores = {
                "semantic_similarity": sem_sim,
                "lexical_similarity": lex_sim,
                "phonetic_similarity": pho_sim
            }
            
            # Dynamic weighting (Lexical + Phonetic focus)
            final_sim = (lex_sim * 0.7) + (pho_sim * 0.3)
            
            # Track conflicts above threshold
            if final_sim > 0.65: # Tighter threshold for lexical matches
                all_conflicts.append(ConflictDetail(
                    title=candidate_title,
                    conflict_type="Lexical/Fuzzy",
                    similarity_score=round(final_sim, 4),
                    highlighted_text=candidate_title # Simple highlight for now
                ))
            
            if final_sim > best_similarity:
                best_similarity = final_sim
                best_match = candidate_title
                best_scores = scores
        
        # 7. Compliance override
        if not compliance_res["is_compliant"] and compliance_res["penalty_score"] >= 1.0:
            best_similarity = 1.0
        
        # 8. Decision
        confidence = self.confidence_scorer.calculate_confidence(best_scores)
        prob = self.probability.compute_probability(best_similarity)
        decision_meta = self.decision.categorize_decision(
            best_similarity, compliance_res["is_compliant"], confidence
        )
        
        # 9. Explanation
        explanation = self.explainer.build_explanation(compliance_res, best_scores, decision_meta["decision"])
        if best_match:
            explanation += f" | Closest match: '{best_match}' ({best_similarity:.2%})"
        if patterns:
            explanation += f" | Patterns: {', '.join(patterns)}"
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        # Sort conflicts by similarity (highest first), limit to top 5
        all_conflicts.sort(key=lambda c: c.similarity_score, reverse=True)
        
        # Prepare analysis detail for the frontend dashboard
        analysis_detail = AnalysisDetail(
            lexical_similarity=int(best_scores.get("lexical_similarity", 0.0) * 100),
            phonetic_similarity=int(best_scores.get("phonetic_similarity", 0.0) * 100),
            semantic_similarity=int(best_scores.get("semantic_similarity", 0.0) * 100),
            disallowed_word=any(v in explanation.lower() for v in ["disallowed", "restricted"]),
            periodicity_violation="periodicity" in explanation.lower(),
            combination_violation="combination" in explanation.lower(),
            prefix_suffix_violation="prefix" in explanation.lower() or "suffix" in explanation.lower()
        )

        result = ComplianceResult(
            is_compliant=compliance_res["is_compliant"] and decision_meta["decision"] != "Reject",
            verification_probability=prob,
            decision=decision_meta["decision"],
            explanation=explanation,
            conflicts=all_conflicts[:5],
            scores=best_scores,
            analysis=analysis_detail,
            metadata={
                "risk_tier": decision_meta["risk_tier"],
                "confidence_score": round(confidence, 4),
                "structural_patterns": patterns,
                "processing_time_ms": elapsed_ms,
                "candidates_checked": len(candidates),
                "best_match": best_match
            }
        )
        
        # 10. Audit
        self.audit_logger.log_verification(title, result.dict())
        
        return result
