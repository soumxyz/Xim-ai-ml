from rapidfuzz.distance import DamerauLevenshtein

class LexicalSimilarityEngine:
    async def calculate_similarity(self, title1: str, title2: str) -> float:
        """
        Calculates similarity using Damerau-Levenshtein distance.
        This handles insertions, deletions, substitutions, and transpositions.
        """
        s1, s2 = title1.lower(), title2.lower()
        distance = DamerauLevenshtein.distance(s1, s2)
        max_len = max(len(s1), len(s2), 1)
        
        # Return similarity (1 - normalized distance)
        return 1.0 - (distance / max_len)
