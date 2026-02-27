import logging
import unicodedata
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
from app.compliance.title_quality_validator import TitleQualityValidator
from app.interpretability.bionic_conflict_highlighter import BionicConflictHighlighter
from app.monitoring.audit_logger import AuditLogger
from app.configuration.scoring_weights import SCORING_WEIGHTS
from app.api.request_models import ComplianceResult, ConflictDetail, AnalysisDetail, SuggestionDetail
from app.intelligence.suggestion_engine import SuggestionEngine
from app.persistence.title_repository import TitleRepository
from app.preprocessing.transliteration_normalizer import TransliterationNormalizer
from metaphone import doublemetaphone

class MetrixaOrchestrator:
    def __init__(self, ann_index=None, token_index=None, sbert_available=False):
        self.normalizer = NormalizationPipeline()
        self.transliteration_normalizer = TransliterationNormalizer()
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
        self.quality_validator = TitleQualityValidator()
        self.audit_logger = AuditLogger()
        self.suggestion_engine = SuggestionEngine()
        self.logger = logging.getLogger("metrixa")

    async def verify(self, title: str, _skip_suggestions: bool = False) -> ComplianceResult:
        start_time = time.time()
        
        # 1. Linguistic Quality Check (Gibberish/Numeric Detection)
        is_low_quality, quality_violations, q_risk = self.quality_validator.validate(title)
        if is_low_quality:
            elapsed_ms = int((time.time() - start_time) * 1000)
            analysis_detail = AnalysisDetail(
                lexical_similarity=0, phonetic_similarity=0, semantic_similarity=0,
                disallowed_word=False, periodicity_violation=False,
                combination_violation=False, prefix_suffix_violation=False
            )
            
            # Linguistic Quality Gate is considered a Hard Violation
            prob = 0.0
            decision = "Reject"
            
            return ComplianceResult(
                is_compliant=False,
                verification_probability=prob,
                decision=decision,
                explanation=f"Linguistic Quality Failure: {'; '.join(quality_violations)}",
                conflicts=[],
                scores={},
                analysis=analysis_detail,
                metadata={
                    "risk_tier": q_risk,
                    "dominant_signal": "Linguistic Quality",
                    "processing_time_ms": elapsed_ms,
                    "candidates_checked": 0,
                    "is_low_quality": True
                }
            )

        # 2. Normalize
        normalized_query = self.normalizer.normalize(title)
        
        # 2. Fetch existing titles for combination detection
        existing_titles = await self.repo.get_all_titles()
        
        # 2.5. Canonical Concatenation / Containment Check (Pre-Token Index Override)
        input_canon = self.normalizer.canonical_form(title)
        for cand_dict in existing_titles:
            cand_title = cand_dict.get("title", "")
            
            # Avoid processing empty or minimal length titles
            if len(cand_title) < 2:
                continue
                
            cand_canon = cand_dict.get("canonical_title", "")
            
            # Length-aware substring and exact match check to prevent small substring noise
            if (input_canon == cand_canon or 
                (len(cand_canon) > 12 and cand_canon in input_canon) or 
                (len(input_canon) > 12 and input_canon in cand_canon)):
                
                elapsed_ms = int((time.time() - start_time) * 1000)
                
                analysis_detail = AnalysisDetail(
                    lexical_similarity=100,
                    phonetic_similarity=100,
                    semantic_similarity=100,
                    disallowed_word=False,
                    periodicity_violation=False,
                    combination_violation=True,
                    prefix_suffix_violation=False
                )
                
                self.logger.info(f"Concatenation clash. '{title}' bypassed spacing but matched '{cand_title}'.")
                
                return ComplianceResult(
                    is_compliant=False,
                    verification_probability=0.0,
                    decision="Reject",
                    explanation=f"Concatenation duplicate detected. Space-agnostic string completely overlaps with existing title '{cand_title}'.",
                    conflicts=[ConflictDetail(
                        title=cand_title,
                        conflict_type="Lexical",
                        similarity_score=1.0,
                        highlighted_text=f'<span class="bionic-wrapper">{title}</span>'
                    )],
                    scores={
                        "semantic_similarity": 1.0,
                        "lexical_similarity": 1.0,
                        "phonetic_similarity": 1.0
                    },
                    analysis=analysis_detail,
                    metadata={
                        "risk_tier": "Critical",
                        "dominant_signal": "Space Bypass / Concatenation",
                        "confidence_score": 1.0,
                        "structural_patterns": [],
                        "processing_time_ms": elapsed_ms,
                        "candidates_checked": len(existing_titles),
                        "best_match": cand_title
                    }
                )
        
        # 3. Compliance check (Deterministic + Combination)
        compliance_res = await self.compliance.check_compliance(title, existing_titles)
        
        # 4. Pattern Detection
        patterns = self.pattern_detector.detect_patterns(title)
        
        # 5. Robust Candidate Retrieval via Token Index (Instant)
        candidates = []
        if self.token_index:
            query_tokens = normalized_query.split()
            
            # Tier 0.5: Transliteration Normalization
            # We search the index using BOTH original tokens and flattened transliterations to guarantee candidate hit
            transliterated_query = self.transliteration_normalizer.normalize(normalized_query)
            all_search_tokens = list(set(query_tokens + transliterated_query.split()))
            
            candidates = await self.token_index.filter_by_tokens(all_search_tokens)
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
        
        # 6. Deep Comparison on Candidates (Hybrid Intelligence)
        from rapidfuzz import fuzz
        from app.intelligence.concept_clusters import calculate_concept_similarity
        
        best_match = None
        best_similarity = 0.0
        all_conflicts = []
        best_scores = {}
        
        # Determine weighting based on title length (Adaptive Weighting)
        words_count = len(title.split())
        w_lex = 0.6 if words_count > 3 else 0.4
        w_pho = 0.3 if words_count > 3 else 0.5
        w_sem = 0.1 # Base semantic weight for cluster/MiniLM
        
        # Score candidates
        query_norm = self.transliteration_normalizer.normalize(title)
        query_canonical = self.normalizer.canonical_form(title)
        
        for candidate in candidates[:50]:
            candidate_title = candidate.get("title", "")
            
            # Apply NFKC Unicode Normalization to protect against invisible characters
            query_lower = unicodedata.normalize('NFKC', title).strip().lower()
            cand_lower = unicodedata.normalize('NFKC', candidate_title).strip().lower()
            cand_norm = self.transliteration_normalizer.normalize(candidate_title)
            cand_canonical = self.normalizer.canonical_form(candidate_title)
            
            # Semantic (Concept Clusters)
            sem_sim = calculate_concept_similarity(query_norm, cand_norm)
            
            # Lexical (Fuzzy Token Set) - Take max of original vs transliterated vs space-stripped
            lex_orig = fuzz.token_set_ratio(query_lower, cand_lower) / 100.0
            lex_norm = fuzz.token_set_ratio(query_norm, cand_norm) / 100.0
            lex_canon = fuzz.token_set_ratio(query_canonical, cand_canonical) / 100.0
            
            # Sub-character 3-gram Match (against space-agnostic concatenation attacks)
            ngram_sim = await self.lexical.calculate_ngram_similarity(title, candidate_title, n=3)
            
            lex_sim = max(lex_orig, lex_norm, lex_canon, ngram_sim)
            
            # Phonetic (Double Metaphone) - Take max of original vs transliterated
            pho_orig = await self.phonetic.calculate_similarity(query_lower, cand_lower)
            pho_norm = await self.phonetic.calculate_similarity(query_norm, cand_norm)
            pho_sim = max(pho_orig, pho_norm)
            
            # -------------------------------------------------------------
            # Multi-Signal Similarity Model (Max-Dominant Hybrid)
            # -------------------------------------------------------------
            # 1. Deterministic Dominant Core
            sim_dominant = max(lex_sim, pho_sim)
            
            # 2. Semantic Dampening (Semantic only assists, doesn't weaken near-duplicates)
            if sim_dominant < 0.95:
                sim_final = 0.7 * sim_dominant + 0.3 * sem_sim
            else:
                sim_final = sim_dominant
                
            # 3. Containment Boost (controlled — 0.10 not 0.15)
            # If the strings are functionally contained within each other, boost the similarity
            # (Note: exact duplicates & canonical bypasses are already caught & rejected earlier)
            containment_flag = 1 if (cand_lower in query_lower or query_lower in cand_lower) else 0
            sim_boosted = min(1.0, sim_final + (0.10 * containment_flag))
            
            # 4. Adaptive Threshold by Title Length (gentle 1.03x, not 1.05x)
            # Short titles represent a mathematically higher absolute risk of violation
            if words_count <= 2:
                sim_boosted = min(1.0, sim_boosted * 1.03)
                
            final_sim = sim_boosted
            
            # Debug logging: intermediate scores for diagnosing binary output
            self.logger.debug(
                f"SCORE '{title}' vs '{candidate_title}': "
                f"L={lex_sim:.4f} Ph={pho_sim:.4f} Sem={sem_sim:.4f} "
                f"dominant={sim_dominant:.4f} final={sim_final:.4f} "
                f"contain={containment_flag} boosted={sim_boosted:.4f} → {final_sim:.4f}"
            )
            
            scores = {
                "semantic_similarity": sem_sim,
                "lexical_similarity": lex_sim,
                "phonetic_similarity": pho_sim
            }
            
            # Track conflicts for Bionic Highlighter (Red/Orange/Yellow)
            if final_sim > 0.60:
                conflict_data = {
                    "tokens": list(set(title.lower().split()) & set(candidate_title.lower().split())),
                    "rules": compliance_res.get("violations_terms", []),
                    "phonetic": [doublemetaphone(w)[0] for w in candidate_title.split()]
                }
                highlighted = self.highlighter.highlight(title, conflict_data)
                
                all_conflicts.append(ConflictDetail(
                    title=candidate_title,
                    conflict_type="Lexical" if lex_sim > pho_sim else "Phonetic",
                    similarity_score=round(final_sim, 4),
                    highlighted_text=highlighted
                ))
            
            if final_sim > best_similarity:
                best_similarity = final_sim
                best_match = candidate_title
                best_scores = scores
        
        # 7. Compliance override (soft — preserves some gradation)
        if not compliance_res["is_compliant"] and compliance_res["penalty_score"] >= 1.0:
            best_similarity = max(best_similarity, 0.95)
        
        # 8. Decision & Risk Tiering
        confidence = self.confidence_scorer.calculate_confidence(best_scores)
        decision_meta = self.decision.categorize_decision(
            best_similarity, compliance_res["is_compliant"], confidence
        )
        
        prob = self.probability.compute_probability(
            best_similarity, 
            compliance_res["is_compliant"], 
            decision_meta["decision"]
        )
        
        # Calculate Dominant Signal
        dominant_val = max(best_scores.values()) if best_scores else 0
        dominant_signal = "None"
        if dominant_val > 0:
            if best_scores.get("lexical_similarity") == dominant_val: dominant_signal = "Lexical Overlap"
            elif best_scores.get("phonetic_similarity") == dominant_val: dominant_signal = "Phonetic Similarity"
            elif best_scores.get("semantic_similarity") == dominant_val: dominant_signal = "Conceptual Similarity"
        
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

        # 9.5. Suggestion Engine (only on Reject/Review, skip during re-scoring)
        suggestions_list = None
        if not _skip_suggestions and decision_meta["decision"] in ("Reject", "Review"):
            try:
                self.logger.info(f"Generating suggestions for rejected title: '{title}'")
                
                # Analyze what caused the conflict
                conflict_dicts = [c.dict() for c in all_conflicts[:5]]
                analysis = self.suggestion_engine.analyze_conflicts(
                    title=title,
                    conflicts=conflict_dicts,
                    best_scores=best_scores,
                    dominant_signal=dominant_signal,
                    compliance_violations=compliance_res.get("violations", []),
                )
                
                # Classify token risk
                token_risks = self.suggestion_engine.classify_token_risk(
                    title.split(), analysis
                )
                self.logger.info(f"Token risks: {token_risks}")
                
                # Generate candidates
                raw_candidates = self.suggestion_engine.generate_candidates(
                    title, analysis, token_risks
                )
                self.logger.info(f"Generated {len(raw_candidates)} raw suggestion candidates")
                
                # Re-score through the full pipeline (with _skip_suggestions=True)
                scored = await self.suggestion_engine.rescore_and_filter(
                    raw_candidates, self, min_probability=10.0, max_results=5
                )
                
                if scored:
                    suggestions_list = [
                        SuggestionDetail(
                            suggested_title=s["suggested_title"],
                            verification_probability=s["verification_probability"],
                            reason=s["reason"],
                        )
                        for s in scored
                    ]
                    self.logger.info(f"Returning {len(suggestions_list)} verified suggestions")
                else:
                    self.logger.info("No suggestions met the probability threshold")
                    
            except Exception as e:
                self.logger.warning(f"Suggestion engine error: {e}")
                suggestions_list = None
        
        elapsed_ms = int((time.time() - start_time) * 1000)  # Recalculate to include suggestion time
        
        result = ComplianceResult(
            is_compliant=compliance_res["is_compliant"] and decision_meta["decision"] != "Reject",
            verification_probability=round(prob, 2),
            decision=decision_meta["decision"],
            explanation=explanation,
            conflicts=all_conflicts[:5],
            scores=best_scores,
            analysis=analysis_detail,
            suggestions=suggestions_list,
            metadata={
                "risk_tier": decision_meta["risk_tier"],
                "dominant_signal": dominant_signal,
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
