import ahocorasick
import re

class PeriodicityValidator:
    def __init__(self):
        self.periodicity_terms = ["daily", "weekly", "monthly", "fortnightly", "annual"]
        self.automaton = ahocorasick.Automaton()
        for term in self.periodicity_terms:
            self.automaton.add_word(term, term)
        self.automaton.make_automaton()

    async def check(self, title: str) -> dict:
        title_lower = title.lower()
        for end_index, term in self.automaton.iter(title_lower):
            start_index = end_index - len(term) + 1
            
            # Simple boundary check for periodicity
            before = title_lower[start_index-1] if start_index > 0 else " "
            after = title_lower[end_index+1] if end_index < len(title_lower) - 1 else " "
            
            if not before.isalnum() and not after.isalnum():
                # Strip the term and extra spaces for 'base title' similarity check
                pattern = rf"\b{term}\b"
                cleaned_title = re.sub(pattern, "", title_lower, flags=re.IGNORECASE).strip()
                cleaned_title = re.sub(r'\s+', ' ', cleaned_title) # Normalize spaces
                
                return {
                    "reason": f"Title contains periodicity term: '{term}'",
                    "term": term,
                    "penalty": 0.5,
                    "cleaned_title": cleaned_title
                }
        return None
