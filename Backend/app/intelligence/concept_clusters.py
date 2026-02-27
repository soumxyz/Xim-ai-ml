"""
Metrixa Concept Cluster Dictionary
Provides a lightweight semantic layer by mapping words to conceptual roots.
Enabled without requiring heavy transformer models.
"""

CONCEPT_CLUSTERS = {
    "morning": ["morning", "dawn", "sunrise", "prabhat", "bhor", "ark", "daybreak", "early", "aurora"],
    "evening": ["evening", "sandhya", "dusk", "sunset", "nightfall", "twilight", "vesper"],
    "news": ["news", "samachar", "khabar", "shabdan", "varta", "bulletin", "report", "dispatch"],
    "daily": ["daily", "dainik", "pratidin", "rozana", "everyday"],
    "weekly": ["weekly", "saptahik", "hafta", "fortnightly"],
    "government": ["governance", "rajya", "shashan", "sarkari", "public", "civic", "national"],
    "crime": ["crime", "police", "scandal", "corruption", "apradh", "justice"],
    "health": ["health", "swasthya", "medical", "ayurved", "vital", "wellness", "wellbeing"],
    "business": ["business", "vyapar", "trade", "commerce", "economy", "enterprise", "market"],
    "sports": ["sports", "khel", "kridan", "stadium", "athletics", "arena"],
    "educational": ["education", "shiksha", "vidya", "study", "learning", "academia", "scholars"],
    "mirror": ["mirror", "darpan", "reflection", "aaina", "lens", "prism"],
    "herald": ["herald", "messenger", "doot", "varta", "post", "courier", "envoy"],
    "chronicle": ["chronicle", "history", "itihas", "patrika", "journal", "annals", "record"],
    "times": ["times", "era", "epoch", "age", "period", "samay"],
    "express": ["express", "rapid", "swift", "flash", "instant"],
    "star": ["star", "stellar", "tara", "luminous", "radiant"],
    "voice": ["voice", "awaaz", "swara", "echo", "resonance"],
    "light": ["light", "prakash", "jyoti", "beacon", "glow", "ray"],
    "truth": ["truth", "satya", "sach", "veritas", "reality"],
}

def get_concept_root(word: str) -> str:
    """Returns the root cluster key if word exists in any cluster."""
    word = word.lower()
    for root, variants in CONCEPT_CLUSTERS.items():
        if word == root or word in variants:
            return root
    return word


def get_cluster_alternatives(word: str) -> list:
    """
    Returns all alternatives for a word from its concept cluster,
    excluding the word itself. Returns empty list if word is not in any cluster.
    """
    word_lower = word.lower()
    for root, variants in CONCEPT_CLUSTERS.items():
        if word_lower == root or word_lower in variants:
            return [v for v in variants if v != word_lower]
    return []

def calculate_concept_similarity(title1: str, title2: str) -> float:
    """
    Checks if titles share conceptual roots.
    Returns 1.0 if they share a cluster root, else 0.0.
    """
    roots1 = {get_concept_root(w) for w in title1.lower().split() if len(w) > 3}
    roots2 = {get_concept_root(w) for w in title2.lower().split() if len(w) > 3}
    
    # Exclude roots that are just the word itself (unless they are cluster keys)
    cluster_roots1 = roots1.intersection(CONCEPT_CLUSTERS.keys())
    cluster_roots2 = roots2.intersection(CONCEPT_CLUSTERS.keys())
    
    intersection = cluster_roots1.intersection(cluster_roots2)
    return 1.0 if intersection else 0.0
