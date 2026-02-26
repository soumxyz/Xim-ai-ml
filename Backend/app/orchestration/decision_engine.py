from app.configuration.threshold_config import COMPLIANCE_THRESHOLDS

class DecisionEngine:
    def categorize_decision(self, final_similarity: float, is_compliant: bool, confidence: float = 1.0) -> dict:
        """
        Categorizes decision into Risk Tiers based on explicit bands.
        """
        if not is_compliant:
            return {"decision": "Reject", "risk_tier": "Critical", "reason": "Policy Violation"}
            
        if final_similarity >= COMPLIANCE_THRESHOLDS["reject"]:
            return {"decision": "Reject", "risk_tier": "High", "reason": "High Similarity Conflict"}
                
        elif final_similarity >= COMPLIANCE_THRESHOLDS["review"]:
            # Band for manual review (65-85)
            tier = "High" if final_similarity > 0.75 else "Medium-High"
            return {"decision": "Review", "risk_tier": tier, "reason": "Potential Overlap - Manual Review Required"}
            
        else:
            return {"decision": "Accept", "risk_tier": "Low", "reason": "Safe"}
