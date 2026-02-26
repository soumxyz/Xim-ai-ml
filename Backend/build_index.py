"""
Offline FAISS index builder.
Run this ONCE (or whenever Dataset.json changes) to prebuild the index.
Usage: python build_index.py
"""
import json
import os
import time
import numpy as np
import faiss

# Ensure we can import the engine
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.intelligence.semantic_similarity_engine import SemanticSimilarityEngine

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATASET_PATH = os.path.join(DATA_DIR, "Dataset.json")
INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.bin")
META_PATH = os.path.join(DATA_DIR, "faiss_metadata.json")


def load_titles():
    titles = []
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            title = row.get("title") or row.get("headline") or "Untitled"
            titles.append({
                "id": row.get("id", len(titles)),
                "title": title,
                "normalized_title": row.get("normalized_title", title.lower())
            })
    return titles


def main():
    print(f"Loading titles from {DATASET_PATH}...")
    titles = load_titles()
    # TRUNCATE FOR TEST BUILD
    titles = titles[:1000] 
    print(f"Loaded {len(titles)} titles for build.")

    sbert = SemanticSimilarityEngine()
    print(f"Loading model: {sbert.model_name}...")
    
    title_texts = [t["title"] for t in titles]
    
    print(f"Encoding {len(title_texts)} titles in small batches...")
    start = time.time()
    # Use even smaller batch size for stability in this environment
    embeddings = sbert.encode_batch(title_texts, batch_size=16) 
    elapsed = time.time() - start
    
    if embeddings is None:
        print("FAILED: Embeddings are None")
        return

    print(f"Encoding complete in {elapsed:.1f}s. Shape: {embeddings.shape}")

    # Build FAISS HNSW index
    dim = embeddings.shape[1]
    index = faiss.IndexHNSWFlat(dim, 32)
    index.hnsw.efConstruction = 40
    index.hnsw.efSearch = 16
    index.add(embeddings)
    print(f"FAISS HNSW index built: {index.ntotal} vectors, dim={dim}")

    # Save index
    faiss.write_index(index, INDEX_PATH)
    print(f"Index saved to {INDEX_PATH}")

    # Save metadata (titles list)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(titles, f, ensure_ascii=False)
    print(f"Metadata saved to {META_PATH}")

    print("Done! The backend will now load this index instantly on startup.")


if __name__ == "__main__":
    main()
