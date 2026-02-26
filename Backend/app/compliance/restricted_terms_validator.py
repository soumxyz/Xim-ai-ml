import ahocorasick

class RestrictedTermsValidator:
    def __init__(self):
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
