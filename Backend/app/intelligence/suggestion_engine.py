"""
Metrixa Suggestion Engine
Generates compliant alternative titles when a submission is rejected or flagged.
Uses conflict-aware token substitution, concept cluster intelligence,
and full pipeline re-scoring to ensure suggestion quality.
"""

import logging
import json
import os
from typing import List, Dict, Tuple, Optional
from metaphone import doublemetaphone

from app.intelligence.concept_clusters import (
    CONCEPT_CLUSTERS,
    get_concept_root,
    get_cluster_alternatives,
)

logger = logging.getLogger("metrixa")

# ---------------------------------------------------------------------------
# Safe word banks — vetted against restricted_terms.json
# ---------------------------------------------------------------------------
SAFE_PREFIXES = [
    "Horizon", "Insight", "Metro", "Prime", "National",
    "Civic", "Pioneer", "Pinnacle", "Frontier", "Apex",
    "Sentinel", "Beacon", "Spectrum", "Vantage", "Meridian",
]

SAFE_SUFFIXES = [
    "Chronicle", "Dispatch", "Bulletin", "Gazette", "Tribune",
    "Observer", "Reporter", "Sentinel", "Review", "Ledger",
    "Journal", "Monitor", "Outlook", "Digest", "Register",
]

# ---------------------------------------------------------------------------
# Blacklist loader (mirrors restricted_terms_validator.py)
# ---------------------------------------------------------------------------
_BLACKLIST: set = set()
_PERIODICITY: set = set()

def _load_blacklists():
    global _BLACKLIST, _PERIODICITY
    if _BLACKLIST:
        return
    json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'restricted_terms.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for key, terms in data.items():
                if key == "periodicity_terms":
                    _PERIODICITY.update(t.lower() for t in terms)
                elif key != "restricted_prefix_suffix":
                    _BLACKLIST.update(t.lower() for t in terms)
    except Exception:
        _BLACKLIST = {"police", "army", "cbi", "cid", "government", "ministry"}
        _PERIODICITY = {"daily", "weekly", "monthly", "morning", "evening", "sunday", "saturday", "annual"}
    # Periodicity terms are also blocked from suggestions
    _BLACKLIST.update(_PERIODICITY)


def _is_safe_word(word: str) -> bool:
    """Returns True if the word is not in any blacklist."""
    _load_blacklists()
    w = word.lower().strip()
    return w not in _BLACKLIST and len(w) >= 2


# ---------------------------------------------------------------------------
# Token Risk Classification
# ---------------------------------------------------------------------------
class TokenRisk:
    SAFE = "SAFE"
    RISKY = "RISKY"
    BLOCKED = "BLOCKED"   # restricted / periodicity term


class SuggestionEngine:
    """
    Generates compliant alternative titles using conflict-aware token substitution.
    """

    def __init__(self):
        _load_blacklists()

    # ------------------------------------------------------------------
    # 1. Conflict Analysis
    # ------------------------------------------------------------------
    def analyze_conflicts(
        self,
        title: str,
        conflicts: List[dict],
        best_scores: Dict[str, float],
        dominant_signal: str,
        compliance_violations: List[str],
    ) -> Dict:
        """
        Returns a structured analysis of what caused the rejection.
        """
        tokens = title.split()
        conflicting_tokens: set = set()

        # Extract conflicting tokens from conflict details
        for conflict in conflicts:
            cand = conflict.get("title", "")
            shared = set(t.lower() for t in tokens) & set(t.lower() for t in cand.split())
            conflicting_tokens.update(shared)

        # Detect periodicity and restricted violations
        has_periodicity = any("periodicity" in v.lower() for v in compliance_violations)
        has_restricted = any("restricted" in v.lower() for v in compliance_violations)
        has_combination = any("combination" in v.lower() for v in compliance_violations)

        # Dominant conflict type
        lex = best_scores.get("lexical_similarity", 0)
        pho = best_scores.get("phonetic_similarity", 0)
        sem = best_scores.get("semantic_similarity", 0)

        if lex >= pho and lex >= sem:
            conflict_type = "lexical"
        elif pho >= lex and pho >= sem:
            conflict_type = "phonetic"
        else:
            conflict_type = "conceptual"

        return {
            "conflict_type": conflict_type,
            "conflicting_tokens": conflicting_tokens,
            "has_periodicity": has_periodicity,
            "has_restricted": has_restricted,
            "has_combination": has_combination,
            "dominant_signal": dominant_signal,
        }

    # ------------------------------------------------------------------
    # 2. Token Risk Classification
    # ------------------------------------------------------------------
    def classify_token_risk(self, tokens: List[str], analysis: Dict) -> List[Tuple[str, str]]:
        """
        Labels each token as SAFE, RISKY, or BLOCKED.
        """
        result = []
        for token in tokens:
            t_lower = token.lower()

            # Blocked: restricted or periodicity term
            if t_lower in _BLACKLIST:
                result.append((token, TokenRisk.BLOCKED))
            # Risky: appears in conflicting tokens or has a concept cluster root
            elif t_lower in analysis["conflicting_tokens"]:
                result.append((token, TokenRisk.RISKY))
            elif get_concept_root(t_lower) != t_lower:
                # Word belongs to a concept cluster — potentially risky
                result.append((token, TokenRisk.RISKY))
            else:
                result.append((token, TokenRisk.SAFE))

        return result

    # ------------------------------------------------------------------
    # 3. Candidate Generation (4 strategies)
    # ------------------------------------------------------------------
    def generate_candidates(
        self,
        title: str,
        analysis: Dict,
        token_risks: List[Tuple[str, str]],
        max_candidates: int = 20,
    ) -> List[Dict]:
        """
        Produces candidate titles via multiple strategies.
        Returns list of {"title": str, "reason": str}.
        """
        candidates = []
        seen_titles: set = set()
        tokens = [t for t, _ in token_risks]

        def _add(new_title: str, reason: str):
            key = new_title.strip().lower()
            if key not in seen_titles and _title_is_clean(new_title) and len(candidates) < max_candidates:
                seen_titles.add(key)
                candidates.append({"title": _titlecase(new_title), "reason": reason})

        # Strategy A — Concept Cluster Swap
        for i, (tok, risk) in enumerate(token_risks):
            if risk in (TokenRisk.RISKY, TokenRisk.BLOCKED):
                alternatives = get_cluster_alternatives(tok)
                for alt in alternatives[:4]:
                    if _is_safe_word(alt):
                        new_tokens = tokens[:i] + [alt.capitalize()] + tokens[i+1:]
                        _add(" ".join(new_tokens), f"Replaced '{tok}' with cluster alternative '{alt.capitalize()}'")

        # Strategy B — Safe Suffix Substitution
        # If last token is risky/blocked, replace with safe suffixes
        if token_risks and token_risks[-1][1] in (TokenRisk.RISKY, TokenRisk.BLOCKED):
            safe_tokens = [t for t, r in token_risks[:-1] if r == TokenRisk.SAFE]
            base = " ".join(safe_tokens) if safe_tokens else tokens[0]
            for suffix in SAFE_SUFFIXES[:6]:
                _add(f"{base} {suffix}", f"Replaced '{token_risks[-1][0]}' with safe suffix '{suffix}'")

        # Also try replacing the first token if it's risky
        if token_risks and token_risks[0][1] in (TokenRisk.RISKY, TokenRisk.BLOCKED) and len(token_risks) > 1:
            safe_tail = " ".join(t for t, r in token_risks[1:] if r == TokenRisk.SAFE)
            if safe_tail:
                for prefix in SAFE_PREFIXES[:5]:
                    _add(f"{prefix} {safe_tail}", f"Replaced '{token_risks[0][0]}' with safe prefix '{prefix}'")

        # Strategy C — Safe Prefix Injection (when most tokens are risky)
        risky_count = sum(1 for _, r in token_risks if r != TokenRisk.SAFE)
        if risky_count >= len(token_risks) * 0.6:
            safe_remaining = [t for t, r in token_risks if r == TokenRisk.SAFE]
            if safe_remaining:
                base = " ".join(safe_remaining)
            else:
                # All tokens are risky — use only the first safe-to-use token
                base = tokens[0] if _is_safe_word(tokens[0]) else ""

            if base:
                for prefix in SAFE_PREFIXES[:5]:
                    for suffix in SAFE_SUFFIXES[:3]:
                        _add(f"{prefix} {base} {suffix}", f"Reframed as '{prefix} {base} {suffix}' to avoid conflicts")
                        if len(candidates) >= max_candidates:
                            break

        # Strategy D — Phonetic Divergence
        if analysis["conflict_type"] == "phonetic":
            for i, (tok, risk) in enumerate(token_risks):
                if risk == TokenRisk.RISKY:
                    # Pick alternatives that are phonetically different
                    tok_meta = doublemetaphone(tok)[0]
                    alts = get_cluster_alternatives(tok)
                    for alt in alts:
                        alt_meta = doublemetaphone(alt)[0]
                        if alt_meta != tok_meta and _is_safe_word(alt):
                            new_tokens = tokens[:i] + [alt.capitalize()] + tokens[i+1:]
                            _add(" ".join(new_tokens), f"Phonetically diverged: '{tok}' → '{alt.capitalize()}'")

        # Strategy E — Periodicity removal + suffix substitution
        if analysis["has_periodicity"]:
            non_period_tokens = [t for t in tokens if t.lower() not in _PERIODICITY]
            if non_period_tokens:
                base = " ".join(non_period_tokens)
                _add(base, "Removed periodicity term")
                for suffix in SAFE_SUFFIXES[:4]:
                    _add(f"{base} {suffix}", f"Removed periodicity term, added '{suffix}'")

        return candidates

    # ------------------------------------------------------------------
    # 4. Re-score and Filter (called by orchestrator)
    # ------------------------------------------------------------------
    async def rescore_and_filter(
        self,
        candidates: List[Dict],
        orchestrator,
        min_probability: float = 50.0,
        max_results: int = 5,
    ) -> List[Dict]:
        """
        Runs each candidate through the full verification pipeline.
        Only keeps candidates that get an 'Accept' decision.
        """
        scored = []

        for candidate in candidates:
            try:
                # Call verify with _skip_suggestions=True to prevent recursion
                result = await orchestrator.verify(candidate["title"], _skip_suggestions=True)
                prob = result.verification_probability
                decision = result.decision

                # Only return suggestions that would actually be Accepted
                if decision == "Accept" and prob >= min_probability:
                    scored.append({
                        "suggested_title": candidate["title"],
                        "verification_probability": round(prob, 2),
                        "reason": candidate["reason"],
                    })

                    if len(scored) >= max_results:
                        break

            except Exception as e:
                logger.warning(f"Failed to re-score suggestion '{candidate['title']}': {e}")
                continue

        # Sort by probability descending
        scored.sort(key=lambda x: x["verification_probability"], reverse=True)
        return scored[:max_results]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _title_is_clean(title: str) -> bool:
    """Checks that a generated title doesn't contain blacklisted words."""
    _load_blacklists()
    words = title.lower().split()
    for w in words:
        if w in _BLACKLIST:
            return False
    if len(title.strip()) < 3:
        return False
    return True


def _titlecase(s: str) -> str:
    """Smart title-case that preserves already-capitalized words."""
    return " ".join(w.capitalize() if w.islower() else w for w in s.split())
