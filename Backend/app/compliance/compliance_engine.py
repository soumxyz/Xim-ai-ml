from app.compliance.restricted_terms_validator import RestrictedTermsValidator
from app.compliance.prefix_suffix_validator import PrefixSuffixValidator
from app.compliance.periodicity_validator import PeriodicityValidator
from app.compliance.title_combination_detector import TitleCombinationDetector

class ComplianceEngine:
    def __init__(self):
        self.validators = {
            "restricted": RestrictedTermsValidator(),
            "prefix": PrefixSuffixValidator(),
            "periodicity": PeriodicityValidator(),
            "combination": TitleCombinationDetector()
        }

    async def check_compliance(self, title: str, existing_titles: list = None) -> dict:
        results = {
            "is_compliant": True,
            "violations": [],
            "violations_terms": [], # Track terms for Bionic highlighting
            "penalty_score": 0.0,
            "cleaned_titles": []    # Base titles for dual-pass similarity (Phase 10)
        }
        
        # Run standard validators
        for name, validator in self.validators.items():
            if name == "combination":
                if existing_titles:
                    violation = await validator.check(title, existing_titles)
                else:
                    continue
            else:
                violation = await validator.check(title)
                
            if violation:
                results["is_compliant"] = False
                results["violations"].append(violation["reason"])
                if "term" in violation:
                    results["violations_terms"].append(violation["term"])
                if "components" in violation:
                    results["violations_terms"].extend(violation["components"])
                if "cleaned_title" in violation:
                    results["cleaned_titles"].append(violation["cleaned_title"])
                    
                results["penalty_score"] += violation.get("penalty", 0.0)
                
        return results
