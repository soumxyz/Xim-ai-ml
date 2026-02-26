import re

class StructuralPatternDetector:
    def __init__(self):
        self.templates = {
            "TimeBased": r"^(morning|evening|daily|weekly|dawn|dusk|sunrise|sunset)\s+\w+",
            "LocationBased": r"^(indian|bharat|hindu|national|global)\s+\w+",
            "PublicationType": r".*\s+(chronicle|express|herald|times|news|diary|post|journal|mail)$"
        }

    def detect_patterns(self, title: str) -> list:
        found = []
        t_lower = title.lower()
        for name, pattern in self.templates.items():
            if re.search(pattern, t_lower):
                found.append(name)
        return found
