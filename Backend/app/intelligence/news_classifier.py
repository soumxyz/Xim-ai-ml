"""
News Category Classification Engine.

Loads the trained TF-IDF + LinearSVC model and provides prediction methods.
"""

import os
import re
import logging
import numpy as np
import joblib


logger = logging.getLogger("metrixa")

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


class NewsClassifier:
    """Wrapper around the trained news category classifier."""

    def __init__(self):
        model_path = os.path.join(MODELS_DIR, "news_classifier_model.joblib")
        tfidf_path = os.path.join(MODELS_DIR, "news_tfidf_vectorizer.joblib")
        labels_path = os.path.join(MODELS_DIR, "news_label_encoder.joblib")

        if not all(os.path.exists(p) for p in [model_path, tfidf_path, labels_path]):
            raise FileNotFoundError(
                "Model artifacts not found. Run `python train_classifier.py` first."
            )

        self.model = joblib.load(model_path)
        self.tfidf = joblib.load(tfidf_path)
        self.label_encoder = joblib.load(labels_path)
        self.categories = list(self.label_encoder.classes_)

        logger.info(
            f"NewsClassifier loaded: {len(self.categories)} categories"
        )

    @staticmethod
    def _clean_text(text: str) -> str:
        """Basic text cleaning matching training pipeline."""
        text = text.lower()
        text = re.sub(r"http\S+|www\.\S+", "", text)
        text = re.sub(r"[^a-z0-9\s\-']", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def predict(self, headline: str, description: str = "") -> dict:
        """
        Predict the category for a single article.

        Returns:
            dict with keys: category, confidence, top_predictions
        """
        combined = self._clean_text(f"{headline} {description}")
        X = self.tfidf.transform([combined])

        # Get predicted label
        pred_idx = self.model.predict(X)[0]
        category = self.label_encoder.inverse_transform([pred_idx])[0]

        # Get probabilities for all classes
        probas = self.model.predict_proba(X)[0]
        confidence = float(probas[pred_idx])

        # Top-5 predictions
        top_indices = np.argsort(probas)[::-1][:5]
        top_predictions = [
            {
                "category": self.label_encoder.inverse_transform([idx])[0],
                "confidence": round(float(probas[idx]), 4),
            }
            for idx in top_indices
        ]

        return {
            "category": category,
            "confidence": round(confidence, 4),
            "top_predictions": top_predictions,
        }

    def predict_batch(self, articles: list) -> list:
        """
        Predict categories for a batch of articles.

        Args:
            articles: list of dicts with 'headline' and optional 'description'

        Returns:
            list of prediction dicts
        """
        texts = [
            self._clean_text(
                f"{a.get('headline', '')} {a.get('description', '')}"
            )
            for a in articles
        ]
        X = self.tfidf.transform(texts)
        pred_indices = self.model.predict(X)
        probas = self.model.predict_proba(X)

        results = []
        for i, idx in enumerate(pred_indices):
            category = self.label_encoder.inverse_transform([idx])[0]
            confidence = float(probas[i][idx])
            results.append({
                "category": category,
                "confidence": round(confidence, 4),
            })

        return results
