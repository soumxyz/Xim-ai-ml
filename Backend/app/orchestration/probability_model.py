class ProbabilityModel:
    def compute_probability(self, similarity: float, is_compliant: bool = True, decision: str = "Accept") -> float:

        base_prob = 100.0 * (1.0 - similarity)

        if not is_compliant:
            prob = min(base_prob, 5.0)
        elif decision == "Reject":
            prob = base_prob * 0.5
        elif decision == "Review":
            prob = base_prob * 0.75
        else:
            prob = base_prob
        return max(0.0, min(100.0, prob))
