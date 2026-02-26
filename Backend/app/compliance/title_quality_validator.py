import math
from typing import Dict, List, Tuple
import regex as re

class TitleQualityValidator:
    """
    Multilingual Quality Validator (Tier 0 Linguistic Gate)
    Robustly handles English, Devanagari, Odia, and transliterated Indic titles.
    Blocks extreme randomness and meaningless symbols but permits valid linguistic variations.
    """
    
    def __init__(self):
        # English dictionary baseline
        self.english_roots = {
            "news", "times", "herald", "chronicle", "express",
            "daily", "morning", "evening", "today", "journal",
            "the", "india", "observer", "standard", "tribune", 
            "national", "global", "citizen", "mirror", "post", 
            "mail", "bulletin", "gazette", "weekly", "monthly", 
            "reporter", "press", "media", "insight", "review", 
            "world", "state", "city", "local", "region"
        }

        # Transliterated Hindi Roots
        self.hindi_roots = {
            "samachar", "bharat", "dainik", "nav", "pratidin",
            "sandhya", "aaj", "lok", "rajya", "jan", "dhwani",
            "pratidhwani", "hindustan", "nagar", "khabar", 
            "prabhat", "patrika"
        }

        # Transliterated Odia Roots
        self.odia_roots = {
            "sambad", "samaja", "odisha", "khabar",
            "barta", "pratidin", "sakal"
        }

    def calculate_shannon_entropy(self, text: str) -> float:
        """Calculates the Shannon entropy to detect keyboard-mashing."""
        if not text:
            return 0.0
        import collections
        counts = collections.Counter(text.lower())
        probs = [count / len(text) for count in counts.values()]
        return -sum(p * math.log2(p) for p in probs)

    def detect_script(self, text: str) -> str:
        """Detects the dominant script using Unicode properties."""
        if re.search(r'\p{Devanagari}', text):
            return "devanagari"
        if re.search(r'\p{Oriya}', text):
            return "odia"
        if re.search(r'[a-zA-Z]', text):
            return "latin"
        return "unknown"

    def validate(self, title: str) -> Tuple[bool, List[str], str]:
        """
        Validates the linguistic quality of a title. (Tier 0 Gate)
        Returns: (is_low_quality, violations, risk_recommendation)
        """
        violations = []
        clean_title = title.strip()
        
        # 1. HARD GARBAGE SANITY CHECKS (Language-Agnostic)
        
        # A. Minimum Character Rule
        # We want to allow 2-letter words like "Ok" or "Hi" if valid, but total length < 3 is risky if alphabet.
        # However, checking alphabet count natively:
        letters = sum(c.isalpha() for c in clean_title)
        if letters < 3 and len(clean_title) <= 3:
            violations.append("Too few alphabetic characters (min 3 required).")
            return True, violations, "Critical"

        # B. Digit Ratio Rule (e.g., catching 82180128201hi)
        digits = sum(c.isdigit() for c in clean_title)
        if len(clean_title) > 0 and (digits / len(clean_title)) > 0.5:
            violations.append(f"Excessive numeric content (Ratio: {(digits/len(clean_title)):.2f}).")
            return True, violations, "Critical"

        # C. Entropy Limit (Extreme Randomness)
        entropy = self.calculate_shannon_entropy(clean_title)
        if entropy > 4.5 and len(clean_title) > 8:
            violations.append(f"High entropy detected (Extreme Randomness: {entropy:.2f}).")
            return True, violations, "High"

        # D. Symbol Overload
        # \p{L}: Letters, \p{N}: Numbers, \p{M}: Marks (like Devanagari matras)
        symbols = re.findall(r'[^\p{L}\p{M}\p{N}\s]', clean_title) 
        if len(clean_title) > 0 and (len(symbols) / len(clean_title)) > 0.3:
            violations.append("Excessive non-alphanumeric characters.")
            return True, violations, "High"

        # 2. SCRIPT-SPECIFIC LINGUISTIC ACCEPTANCE
        script = self.detect_script(clean_title)
        
        # If the text uses Devanagari or Odia and passed the rigorous sanity checks above, 
        # it strongly indicates genuine linguistic intent. We automatically pass it safely.
        if script in ["devanagari", "odia"]:
            return False, [], "Low"

        # 3. LATIN (ENGLISH/TRANSLITERATED) SOFT SCORING MODEL
        linguistic_score = 0.0
        tokens = clean_title.lower().split()

        # D. Character Variety (Repetitive Spam Catch for Latin)
        # Prevents "asdasd" from passing the soft score 
        stripped_title = clean_title.lower().replace(" ", "")
        distinct_chars = len(set(stripped_title))
        if len(stripped_title) >= 5 and (distinct_chars / len(stripped_title)) <= 0.5:
            violations.append("Low character variety detected (repetitive pattern).")
            return True, violations, "Medium"

        # Feature 1: Valid Root Detection
        has_english_root = any(t in self.english_roots for t in tokens)
        has_indic_root = any(t in self.hindi_roots or t in self.odia_roots for t in tokens)
        
        if has_indic_root or has_english_root:
            linguistic_score += 0.4
            
        # Feature 2: Latin Phonotactics
        if script == "latin":
            alpha_chars = [c.lower() for c in clean_title if c.isalpha()]
            if alpha_chars:
                vowels = "aeiou"
                v_ratio = sum(c in vowels for c in alpha_chars) / len(alpha_chars)
                if v_ratio >= 0.20:
                    linguistic_score += 0.3
                else:
                    violations.append(f"Unnatural vowel distribution (Ratio: {v_ratio:.2f}).")
            else:
                violations.append("No Latin alphabetic characters found despite Latin script detection.")

        # Feature 3: Reasonable Entropy Boost
        if entropy <= 4.2:
            linguistic_score += 0.2

        # 4. DECISION LOGIC
        # Threshold 0.5 passes. (Since base pass entropy adds 0.2, they only need 0.3 more,
        # which means a valid vowel ratio makes it 0.5 AND passes safely). 
        if linguistic_score >= 0.5:
            return False, [], "Low"
            
        # Borderline / Failure
        violations.append(f"Failed Linguistic Confidence Threshold (Score: {linguistic_score:.2f}).")
        
        if linguistic_score <= 0.2:
            return True, violations, "High"
        else:
            return True, violations, "Medium"
