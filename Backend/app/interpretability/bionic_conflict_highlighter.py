import re
import math
from metaphone import doublemetaphone

class BionicConflictHighlighter:
    def __init__(self, intensity: float = 0.5, coverage: float = 0.4):
        self.intensity = intensity
        self.coverage = coverage
        self.min_word_len = 3
        
        # Bionic Algorithm Constants (from ref code)
        self.small_word_threshold = 3
        self.small_word_ratio = 0.66
        self.function_word_ratio = 0.35
        self.content_word_ratio = 0.5
        
        # English function words for prioritization
        self.function_words = {
            'a', 'an', 'the', 'in', 'on', 'at', 'by', 'for', 'with', 'from', 'to', 'of',
            'and', 'but', 'or', 'so', 'it', 'its', 'is', 'are', 'was', 'were', 'be'
        }

    def _get_fixation_weight(self) -> int:
        """Computes font-weight based on coverage (intensity)."""
        return round(400 + (self.intensity * 500))

    def _transform_word(self, word: str, force_bionic: bool = False) -> str:
        """
        Transforms a word into bionic format if it's a conflict token or forced.
        Uses the fixation algorithm to bold the initial portion.
        """
        if len(word) < 2:
            return word
            
        clean_word = re.sub(r'[^a-zA-Z]', '', word)
        if not clean_word:
            return word
            
        n = len(clean_word)
        is_function = clean_word.lower() in self.function_words
        
        # Determine bold ratio
        if n <= self.small_word_threshold:
            base_ratio = self.small_word_ratio
        else:
            base_ratio = self.function_word_ratio if is_function else self.content_word_ratio
            
        # Scale by intensity
        scaled_ratio = min(0.95, max(0.05, base_ratio * (0.5 + self.intensity)))
        bold_count = max(1, math.ceil(n * scaled_ratio))
        
        weight = self._get_fixation_weight()
        
        # Construct bionic HTML
        # Using <b> for legacy or <span class="bionic-fixation"> for advanced CSS
        bold_part = word[:bold_count]
        rest_part = word[bold_count:]
        
        return f'<span class="bionic-fixation" style="font-weight:{weight}">{bold_part}</span>{rest_part}'

    def highlight(self, text: str, conflicts: dict) -> str:
        """
        Applies bionic-style highlighting to conflict tokens.
        """
        words = text.split()
        conflict_tokens = set([t.lower() for t in conflicts.get("tokens", [])])
        rule_violations = set([t.lower() for t in conflicts.get("rules", [])])
        phonetic_targets = set(conflicts.get("phonetic", []))
        
        processed_words = []
        for word in words:
            clean = re.sub(r'[^a-zA-Z]', '', word).lower()
            m_code = doublemetaphone(clean)[0]
            
            is_conflict = (
                clean in conflict_tokens or 
                clean in rule_violations or 
                m_code in phonetic_targets or
                any(v in clean for v in rule_violations)
            )
            
            if is_conflict:
                processed_words.append(self._transform_word(word))
            else:
                processed_words.append(word)
                
        highlighted = " ".join(processed_words)
        return f'<span class="bionic-wrapper">{highlighted}</span>'
