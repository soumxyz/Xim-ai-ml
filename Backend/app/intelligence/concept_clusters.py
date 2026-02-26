"""
Metrixa Concept Cluster Dictionary
Provides a lightweight semantic layer by mapping words to conceptual roots.
Enabled without requiring heavy transformer models.
"""

CONCEPT_CLUSTERS = {
    "morning": ["morning", "dawn", "sunrise", "prabhat", "bhor", "ark"],
    "evening": ["evening", "sandhya", "dusk", "sunset", "nightfall"],
    "news": ["news", "samachar", "khabar", "shabdan", "varta"],
    "daily": ["daily", "dainik", "pratidin", "rozana"],
    "weekly": ["weekly", "saptahik", "hafta"],
    "government": ["governance", "rajya", "shashan", "sarkari", "public"],
    "crime": ["crime", "police", "scandal", "corruption", "apradh"],
    "health": ["health", "swasthya", "medical", "ayurved", "vital"],
    "business": ["business", "vyapar", "trade", "commerce", "economy"],
    "sports": ["sports", "khel", "kridan", "stadium"],
    "educational": ["education", "shiksha", "vidya", "study", "learning"],
    "mirror": ["mirror", "darpan", "reflection", "aaina"],
    "herald": ["herald", "messenger", "doot", "varta", "post"],
    "chronicle": ["chronicle", "history", "itihas", "patrika", "journal"]
}

def get_concept_root(word: str) -> str:
    """Returns the root cluster key if word exists in any cluster."""
    word = word.lower()
    for root, variants in CONCEPT_CLUSTERS.items():
        if word == root or word in variants:
            return root
    return word

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
