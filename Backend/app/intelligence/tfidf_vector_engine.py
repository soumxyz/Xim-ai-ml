from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class TFIDFVectorEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.is_fitted = False

    async def calculate_similarity(self, title1: str, title2: str) -> float:
        try:
            tfidf_matrix = self.vectorizer.fit_transform([title1, title2])
            return float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
        except:
            return 0.0
