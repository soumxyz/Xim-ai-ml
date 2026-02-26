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
from app.api.request_models import ComplianceResult, ConflictDetail
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
        
        # 5. REAL Candidate Retrieval via FAISS (or Token Index Fallback)
        candidates = []
        if self.sbert_available and self.ann_index and self.ann_index.index.ntotal > 0:
            query_embedding = self.semantic.encode(title)
            if query_embedding is not None:
                import numpy as np
                candidates = await self.ann_index.get_top_candidates(
                    np.array(query_embedding), top_k=50
                )
                self.logger.info(f"FAISS returned {len(candidates)} candidates for '{title}'")
        
        # Fallback: if FAISS unavailable, use token index
        if not candidates and self.token_index:
            query_tokens = normalized_query.split()
            candidates = await self.token_index.filter_by_tokens(query_tokens)
            self.logger.info(f"Token index fallback: {len(candidates)} candidates")
        
        # If still no candidates, return clean accept
        if not candidates:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return ComplianceResult(
                is_compliant=compliance_res["is_compliant"],
                verification_probability=100.0 if compliance_res["is_compliant"] else 0.0,
                decision="Reject" if not compliance_res["is_compliant"] else "Accept",
                explanation="No similar titles found in database." if compliance_res["is_compliant"] else "; ".join(compliance_res["violations"]),
                conflicts=[],
                scores={},
                metadata={
                    "risk_tier": "Critical" if not compliance_res["is_compliant"] else "Low",
                    "processing_time_ms": elapsed_ms,
                    "candidates_checked": 0
                }
            )
        
        # 6. Deep Comparison on Top Candidates
        best_match = None
        best_similarity = 0.0
        all_conflicts = []
        best_scores = {}
        
        for candidate in candidates[:10]:  # Deep score top 10
            candidate_title = candidate.get("title", "")
            
            # Pass 1: Original title
            if self.sbert_available:
                sem_sim = await self.semantic.calculate_similarity(title, candidate_title)
            else:
                sem_sim = 0.0  # SBERT unavailable, rely on lexical + phonetic
            lex_sim = await self.lexical.calculate_similarity(title, candidate_title)
            pho_sim = await self.phonetic.calculate_similarity(title, candidate_title)
            
            # Pass 2: Cleaned base titles (dual-pass)
            for cleaned in compliance_res.get("cleaned_titles", []):
                if self.sbert_available:
                    sem_c = await self.semantic.calculate_similarity(cleaned, candidate_title)
                else:
                    sem_c = 0.0
                lex_c = await self.lexical.calculate_similarity(cleaned, candidate_title)
                pho_c = await self.phonetic.calculate_similarity(cleaned, candidate_title)
                sem_sim = max(sem_sim, sem_c)
                lex_sim = max(lex_sim, lex_c)
                pho_sim = max(pho_sim, pho_c)
            
            scores = {
                "semantic_similarity": sem_sim,
                "lexical_similarity": lex_sim,
                "phonetic_similarity": pho_sim
            }
            
            # Dynamic weighting
            weights = self.dynamic_scorer.adjust_weights(title, [candidate_title], scores)
            final_sim = (
                sem_sim * weights.get("semantic_similarity", 0.6) +
                pho_sim * weights.get("phonetic_similarity", 0.25) +
                lex_sim * weights.get("lexical_similarity", 0.15)
            )
            
            # Agreement boost
            final_sim = self.dynamic_scorer.apply_agreement_boost(final_sim, scores)
            
            # Track conflicts above threshold
            if final_sim > 0.40:
                conflict_data = {
                    "tokens": list(set(title.lower().split()) & set(candidate_title.lower().split())),
                    "rules": compliance_res.get("violations_terms", []),
                    "phonetic": [doublemetaphone(w)[0] for w in candidate_title.split()]
                }
                highlighted = self.highlighter.highlight(title, conflict_data)
                
                all_conflicts.append(ConflictDetail(
                    title=candidate_title,
                    conflict_type="Semantic" if sem_sim > pho_sim else "Phonetic",
                    similarity_score=round(final_sim, 4),
                    highlighted_text=highlighted
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
        
        result = ComplianceResult(
            is_compliant=compliance_res["is_compliant"] and decision_meta["decision"] != "Reject",
            verification_probability=prob,
            decision=decision_meta["decision"],
            explanation=explanation,
            conflicts=all_conflicts[:5],
            scores=best_scores,
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
