import logging

class SemanticSimilarityEngine:
    _model_instance = None # Class-level singleton

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.logger = logging.getLogger("metrixa")

    @property
    def model(self):
        if SemanticSimilarityEngine._model_instance is None:
            try:
                # Local import to prevent startup crash
                from sentence_transformers import SentenceTransformer
                self.logger.info(f"Loading SBERT model: {self.model_name}...")
                SemanticSimilarityEngine._model_instance = SentenceTransformer(self.model_name)
                self.logger.info("SBERT model loaded successfully.")
            except Exception as e:
                self.logger.error(f"CRITICAL: Failed to load SBERT (likely binary conflict): {str(e)}")
                return None
        return SemanticSimilarityEngine._model_instance

    async def calculate_similarity(self, title1: str, title2: str) -> float:
        model = self.model
        if model is None:
            self.logger.warning("SBERT model unavailable. Falling back to 0.0 similarity.")
            return 0.0
            
        try:
            from sentence_transformers import util
            # Encode titles into SBERT embeddings using lazy-loaded model
            embeddings1 = model.encode(title1, convert_to_tensor=True)
            embeddings2 = model.encode(title2, convert_to_tensor=True)
            
            # Compute cosine similarity
            cosine_score = util.cos_sim(embeddings1, embeddings2)
            return float(cosine_score[0][0])
        except Exception as e:
            self.logger.error(f"Semantic similarity calculation failed: {str(e)}")
            return 0.0

    def encode(self, text: str):
        """Encode a single title into a numpy embedding vector for FAISS."""
        model = self.model
        if model is None:
            return None
        try:
            import numpy as np
            return model.encode(text, convert_to_numpy=True).astype('float32')
        except Exception as e:
            self.logger.error(f"Encoding failed: {e}")
            return None

    def encode_batch(self, texts: list):
        """Encode a batch of titles into numpy embedding vectors for FAISS."""
        model = self.model
        if model is None:
            return None
        try:
            import numpy as np
            return model.encode(texts, convert_to_numpy=True, show_progress_bar=True).astype('float32')
        except Exception as e:
            self.logger.error(f"Batch encoding failed: {e}")
            return None
