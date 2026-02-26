import json
import os

class PrefixSuffixValidator:
    def __init__(self):
        self.restricted_prefixes = ["test-", "prod-"]
        self.restricted_suffixes = ["-beta", "-dev"]
        
        json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'restricted_terms.json')
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "restricted_prefix_suffix" in data:
                    terms = [t.lower() for t in data["restricted_prefix_suffix"]]
                    self.restricted_prefixes.extend(terms)
                    self.restricted_suffixes.extend(terms)
        except Exception:
            pass

    async def check(self, title: str) -> dict:
        title_lower = title.lower()
        cleaned_title = title_lower
        violations = []
        
        for prefix in self.restricted_prefixes:
            if title_lower.startswith(prefix):
                violations.append(f"Title starts with restricted prefix: {prefix}")
                cleaned_title = cleaned_title[len(prefix):].strip()
        
        for suffix in self.restricted_suffixes:
            if title_lower.endswith(suffix):
                violations.append(f"Title ends with restricted suffix: {suffix}")
                cleaned_title = cleaned_title[:-len(suffix)].strip()
        
        if violations:
            return {
                "reason": " | ".join(violations),
                "penalty": 0.2 * len(violations),
                "cleaned_title": cleaned_title
            }
        return None
