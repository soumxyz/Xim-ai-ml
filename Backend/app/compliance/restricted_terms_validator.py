import ahocorasick
import json
import os

class RestrictedTermsValidator:
    def __init__(self):
        self.blacklist = []
        json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'restricted_terms.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for key, terms in data.items():
                    if key not in ["restricted_prefix_suffix", "periodicity_terms"]:
                        self.blacklist.extend([t.lower() for t in terms])
        except Exception:
            self.blacklist = ["police", "army", "cbi", "cid", "government", "ministry"]
            
        self.automaton = ahocorasick.Automaton()
        for term in self.blacklist:
            self.automaton.add_word(term, term)
        self.automaton.make_automaton()

    async def check(self, title: str) -> dict:
        title_lower = title.lower()
        for end_index, term in self.automaton.iter(title_lower):
            return {
                "reason": f"Title contains restricted term: '{term.upper()}'",
                "term": term,
                "penalty": 1.0
            }
        return None
