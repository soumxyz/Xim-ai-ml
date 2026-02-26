class ProbabilityModel:
    def compute_probability(self, similarity: float) -> float:
        # Probability of acceptance = 100 - similarity
        prob = (1.0 - similarity) * 100
        return max(0.0, min(100.0, prob))
