import regex as re
import logging
try:
    from indic_transliteration import sanscript
    from indic_transliteration.sanscript import transliterate
    INDIC_LIB_AVAILABLE = True
except ImportError:
    INDIC_LIB_AVAILABLE = False

logger = logging.getLogger("metrixa")

class TransliterationNormalizer:
    def __init__(self):
        # Universal flattening mapping for Latin strings
        # Normalizes variations like Bhaarat -> Bharat, Samaachar -> Samachar
        self.TRANSLITERATION_RULES = {
            "aa": "a",
            "ee": "i",
            "oo": "u",
            "ou": "o",
            "bh": "b",
            "dh": "d",
            "th": "t",
            "ph": "f",
            "sh": "s",
            "chh": "ch",
            "ri": "r",
            "tra": "tara"
        }

    def detect_script(self, text: str) -> str:
        """Identifies if the script is Devanagari, Odia, or Latin."""
        if re.search(r'\p{Devanagari}', text):
            return sanscript.DEVANAGARI
        elif re.search(r'\p{Oriya}', text):
            return sanscript.ORIYA
        return "latin"

    def normalize(self, text: str) -> str:
        """
        Converts native scripts to Latin (ITRANS) and applies
        canonical phoneme flattening.
        """
        text = text.lower().strip()
        
        # 1. Native to Latin Conversion
        if INDIC_LIB_AVAILABLE:
            script = self.detect_script(text)
            if script in [sanscript.DEVANAGARI, sanscript.ORIYA]:
                try:
                    # Convert to ITRANS (Ascii transliteration scheme)
                    text = transliterate(text, script, sanscript.ITRANS).lower()
                except Exception as e:
                    logger.warning(f"Indic transliteration failed for {text}: {e}")

        # 2. Canonical Flattening
        for pattern, replacement in self.TRANSLITERATION_RULES.items():
            text = text.replace(pattern, replacement)
            
        return text
