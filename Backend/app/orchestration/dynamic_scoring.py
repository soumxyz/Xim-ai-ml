class DynamicScoringModule:
    def adjust_weights(self, title: str, candidates: list, initial_scores: dict) -> dict:
        """
        Dynamically adjusts similarity weights based on observed patterns (Lean 6+ Refinements).
        """
        # Lean 6 Default Weights
        weights = {
            "semantic_similarity": 0.60,
            "phonetic_similarity": 0.25,
            "lexical_similarity": 0.15
        }
        
        words = title.split()
        
        # 1. Short-Title Optimization (< 3 tokens)
        # SBERT can be noisy with 1-2 words; prioritize surface similarity
        if len(words) < 3:
            weights["semantic_similarity"] -= 0.15
            weights["phonetic_similarity"] += 0.10
            weights["lexical_similarity"] += 0.05
            
        # 2. High Phonetic Accuracy Boost
        # If phonetic is extremely high (>0.9), it's a strong indicator
        if initial_scores.get("phonetic_similarity", 0) > 0.90:
            weights["phonetic_similarity"] += 0.15
            weights["semantic_similarity"] -= 0.15
            
        # Normalize weights to sum to 1.0
        total = sum(weights.values())
        return {k: v/total for k, v in weights.items()}

    def apply_agreement_boost(self, final_similarity: float, initial_scores: dict) -> float:
        """
        Applies a confidence boost if multiple engines strongly agree.
        If Semantic > 0.85 AND Phonetic > 0.8, boost final score.
        """
        sem = initial_scores.get("semantic_similarity", 0)
        pho = initial_scores.get("phonetic_similarity", 0)
        
        if sem > 0.85 and pho > 0.80:
            # Apply a 5% boost to similarity (capping at 1.0)
            return min(1.0, final_similarity * 1.05)
            
        return final_similarity
