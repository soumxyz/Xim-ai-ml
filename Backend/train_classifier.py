"""
Train a news category classifier on the HuffPost Dataset.json.

Uses TF-IDF features on headline + short_description with a LinearSVC model.
Saves trained model artifacts to app/models/.
"""

import json
import os
import re
import numpy as np
from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib


# ─── 1. Configuration ────────────────────────────────────────────────────────

DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "Dataset.json")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "app", "models")

# Merge overlapping / duplicate categories
CATEGORY_MERGE_MAP = {
    "ARTS": "ARTS & CULTURE",
    "ARTS & CULTURE": "ARTS & CULTURE",
    "CULTURE & ARTS": "ARTS & CULTURE",
    "STYLE": "STYLE & BEAUTY",
    "STYLE & BEAUTY": "STYLE & BEAUTY",
    "THE WORLDPOST": "WORLD NEWS",
    "WORLDPOST": "WORLD NEWS",
    "WORLD NEWS": "WORLD NEWS",
    "PARENTS": "PARENTING",
    "PARENTING": "PARENTING",
    "TASTE": "FOOD & DRINK",
    "FOOD & DRINK": "FOOD & DRINK",
    "GREEN": "ENVIRONMENT",
    "ENVIRONMENT": "ENVIRONMENT",
    "HEALTHY LIVING": "WELLNESS",
    "WELLNESS": "WELLNESS",
}


# ─── 2. Data Loading & Cleaning ──────────────────────────────────────────────

def load_dataset(path: str) -> list:
    """Load JSONL dataset, filtering out incomplete records."""
    records = []
    skipped = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                skipped += 1
                continue

            headline = (obj.get("headline") or "").strip()
            category = (obj.get("category") or "").strip()
            description = (obj.get("short_description") or "").strip()

            if not headline or not category:
                skipped += 1
                continue

            # Merge overlapping categories
            category = CATEGORY_MERGE_MAP.get(category, category)

            records.append({
                "headline": headline,
                "description": description,
                "category": category,
            })

    print(f"Loaded {len(records)} records ({skipped} skipped)")
    return records


def clean_text(text: str) -> str:
    """Basic text cleaning."""
    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", "", text)  # remove URLs
    text = re.sub(r"[^a-z0-9\s\-']", " ", text)   # keep alphanumeric + hyphens
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ─── 3. Training Pipeline ────────────────────────────────────────────────────

def train():
    print("=" * 60)
    print("  HuffPost News Category Classifier — Training Pipeline")
    print("=" * 60)

    # Load data
    print("\n[1/5] Loading dataset...")
    records = load_dataset(DATASET_PATH)

    # Show category distribution after merging
    cat_counts = Counter(r["category"] for r in records)
    print(f"\nCategories after merging: {len(cat_counts)}")
    for cat, count in cat_counts.most_common():
        print(f"  {cat}: {count}")

    # Prepare features
    print("\n[2/5] Preparing features (TF-IDF)...")
    texts = [
        clean_text(r["headline"] + " " + r["description"])
        for r in records
    ]
    labels = [r["category"] for r in records]

    # Encode labels
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(labels)
    print(f"  Classes: {len(label_encoder.classes_)}")

    # TF-IDF vectorization
    tfidf = TfidfVectorizer(
        max_features=50000,
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=2,
        max_df=0.95,
        strip_accents="unicode",
    )
    X = tfidf.fit_transform(texts)
    print(f"  Feature matrix shape: {X.shape}")

    # Train/test split
    print("\n[3/5] Splitting data (80/20 stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")

    # Train model
    print("\n[4/5] Training LinearSVC with CalibratedClassifierCV...")
    base_svc = LinearSVC(
        class_weight="balanced",
        max_iter=5000,
        C=1.0,
        random_state=42,
    )
    model = CalibratedClassifierCV(base_svc, cv=3)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n  Overall Accuracy: {accuracy:.4f} ({accuracy*100:.1f}%)")
    print("\n  Classification Report:")
    target_names = label_encoder.classes_
    print(classification_report(y_test, y_pred, target_names=target_names))

    # Save artifacts
    print("\n[5/5] Saving model artifacts...")
    os.makedirs(MODELS_DIR, exist_ok=True)

    model_path = os.path.join(MODELS_DIR, "news_classifier_model.joblib")
    tfidf_path = os.path.join(MODELS_DIR, "news_tfidf_vectorizer.joblib")
    labels_path = os.path.join(MODELS_DIR, "news_label_encoder.joblib")

    joblib.dump(model, model_path)
    joblib.dump(tfidf, tfidf_path)
    joblib.dump(label_encoder, labels_path)

    print(f"  Model:      {model_path}")
    print(f"  Vectorizer: {tfidf_path}")
    print(f"  Labels:     {labels_path}")
    print(f"\n{'=' * 60}")
    print(f"  Training complete! Accuracy: {accuracy*100:.1f}%")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    train()
