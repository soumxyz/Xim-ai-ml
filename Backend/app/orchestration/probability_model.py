class ProbabilityModel:
    def compute_probability(self, similarity: float, is_compliant: bool = True, decision: str = "Accept") -> float:
        """
        Computes verification probability with smooth gradation.
        
        Instead of hard-zeroing on Reject/non-compliant, applies scaled penalties
        so the output spectrum is continuous (e.g. 0%, 3%, 12%, 45%, 85%, 100%).
        """
        # Base probability from similarity — never round until final display
        base_prob = 100.0 * (1.0 - similarity)

        if not is_compliant:
            # Hard compliance violation — heavily penalize but preserve some signal
            prob = min(base_prob, 5.0)
        elif decision == "Reject":
            # High similarity reject — scale down, keeps range ~[0–15]
            prob = base_prob * 0.5
        elif decision == "Review":
            # Review band — moderate penalty, range ~[15–50]
            prob = base_prob * 0.75
        else:
            # Accept — full probability
            prob = base_prob

        # Clamp without rounding (rounding happens at display layer only)
        return max(0.0, min(100.0, prob))
