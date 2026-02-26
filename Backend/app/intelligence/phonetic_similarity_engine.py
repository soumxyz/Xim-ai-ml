from metaphone import doublemetaphone
from difflib import SequenceMatcher

class PhoneticSimilarityEngine:
    async def calculate_similarity(self, title1: str, title2: str) -> float:
        # Get primary and secondary metaphones
        m1 = doublemetaphone(title1)
        m2 = doublemetaphone(title2)
        
        # Compare primary to primary
        sim1 = SequenceMatcher(None, m1[0], m2[0]).ratio()
        
        # Compare combinations (primary to secondary, etc.)
        sim2 = SequenceMatcher(None, m1[0], m2[1] if m2[1] else m2[0]).ratio()
        
        return max(sim1, sim2)
