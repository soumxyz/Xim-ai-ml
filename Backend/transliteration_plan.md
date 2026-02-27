# Transliteration Normalization (Tier 0.5)

## Objective

Convert all inputs into a canonical Latin transliteration, flattening phonetic variations ("Samaachar" -> "Samachar", "Bhaarat" -> "Bharat") to improve similarity matching accuracy and resistance against spelling evasion across Indic languages.

## Architecture Change

1. **Tier 0:** Linguistic Quality Gate (Entropy, Character Ratios, Script Detection).
2. **Tier 0.5 (NEW): Transliteration Normalizer.**
   - If the text is native Devanagari or Odia, convert to Latin.
   - Apply pattern mapping (e.g., "aa" -> "a", "ee" -> "i", "bh" -> "b", "sh" -> "s").
   - Handle Hindi vs Odia edge cases.
3. **Tier 1:** Compliance Validation.
4. **Tier 2/3:** Similarity Checks.

## Tasks

- [ ] Create `TransliterationNormalizer` under `app/preprocessing/transliteration_normalizer.py`
- [ ] Apply native Devanagari translation via `indic_transliteration`
- [ ] Implement Phoneme Flattening mapping (`aa` -> `a`).
- [ ] Integrate into `MeshOrchestrator.verify()`.
- [ ] Add Transliteration variation detection to the Dynamic Explanation system.
