class ConfidenceScorer:
    def calculate_confidence(self, scores: dict) -> float:
        """
        Calculates how 'confident' the system is in its decision.
        High confidence comes from agreement across different similarity types.
        """
        s_val = scores.get("semantic_similarity", 0)
        p_val = scores.get("phonetic_similarity", 0)
        l_val = scores.get("lexical_similarity", 0)
        
        # Standard deviation of scores as a proxy for agreement (lower std = higher agreement)
        vals = [s_val, p_val, l_val]
        avg = sum(vals) / len(vals)
        
        # If all scores are high, confidence is very high
        if avg > 0.8:
            return 0.95
            
        # Agreement check
        agreement = 1.0 - (max(vals) - min(vals))
        
        return max(0.0, min(1.0, agreement))
