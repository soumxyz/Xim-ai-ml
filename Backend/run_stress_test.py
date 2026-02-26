import json
import requests
import time

URL = "http://127.0.0.1:8000/api/v1/verify/"

TEST_CASES = [
    "Hindustaan Times",              # Elongation
    "Hindustan Tymes",               # Spelling error
    "Hindustan Daily Times",         # Padding variation
    "भारत समाचार",                    # Native Hindi Script transliteration
    "Samachar",                      # Short single word variation
    "Sambad",                        # Odia variation
    "Pratidin Sandhya",              # Translation variation
    "Daily Evening",                 # Translation control
    "Hindustan Times\u2002",         # Unicode en-space bypass attempt
    "Hindustan\u202DTimes",          # Unicode direction override bypass attempt
    "hindustantimes",                # Space bypass
    "hindustan-times",               # Hyphen bypass
    "HindustanTimes",                # CamelCase bypass
    "hindustan times ltd",           # Pre/Suffix containment bypass
]

print("=== STARTING STRESS TEST SUITE ===")
for title in TEST_CASES:
    try:
        start = time.time()
        res = requests.post(URL, json={"title": title})
        data = res.json()
        elapsed = int((time.time() - start) * 1000)
        
        prob = data.get("verification_probability", 0)
        action = "✅ APPROVE" if prob > 80 else "❌ REJECT"
        match = data.get("metadata", {}).get("best_match", "None")
        
        print(f"[{elapsed}ms] 📝 '{title}' -> {action} ({prob}%) | Match: {match}")
    except Exception as e:
        print(f"ERROR on '{title}': {e}")
