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

    async def calculate_ngram_similarity(self, title1: str, title2: str, n: int = 3) -> float:
        """
        Calculates Jaccard similarity using character N-grams (default 3-grams).
        Extremely effective against concatenation, hyphenation, and typo attacks.
        J(A,B) = |A ∩ B| / |A ∪ B|
        """
        s1 = title1.lower().replace(" ", "")
        s2 = title2.lower().replace(" ", "")
        
        if not s1 or not s2:
            return 0.0
            
        def get_ngrams(text, n):
            return set(text[i:i+n] for i in range(max(1, len(text)-n+1)))
            
        g1 = get_ngrams(s1, n)
        g2 = get_ngrams(s2, n)
        
        if not g1 and not g2:
            return 0.0
            
        return len(g1.intersection(g2)) / len(g1.union(g2))
