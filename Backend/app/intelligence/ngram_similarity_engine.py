class NGramSimilarityEngine:
    def ngrams(self, text, n=3):
        return [text[i:i+n] for i in range(len(text)-n+1)]

    async def calculate_similarity(self, title1: str, title2: str, n: int = 3) -> float:
        ng1 = set(self.ngrams(title1.lower(), n))
        ng2 = set(self.ngrams(title2.lower(), n))
        
        if not ng1 or not ng2:
            return 0.0
            
        intersection = ng1.intersection(ng2)
        union = ng1.union(ng2)
        
        return len(intersection) / len(union)
