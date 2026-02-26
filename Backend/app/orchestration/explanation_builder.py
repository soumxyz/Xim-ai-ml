class ExplanationBuilder:
    def build_explanation(self, compliance_results: dict, scores: dict, decision: str) -> str:
        reasons = []
        
        if not compliance_results["is_compliant"]:
            reasons.extend(compliance_results["violations"])
        
        if scores.get("semantic_similarity", 0) > 0.8:
            reasons.append("High semantic theme overlap detected with existing titles.")
        
        if scores.get("phonetic_similarity", 0) > 0.9:
            reasons.append("Phonetically identical or very similar to an existing title.")
            
        if not reasons:
            reasons.append("Title passed all initial automated checks.")
            
        return " | ".join(reasons)
