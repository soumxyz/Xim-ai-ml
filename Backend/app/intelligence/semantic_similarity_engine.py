import logging
import torch
import torch.nn.functional as F

class SemanticSimilarityEngine:
    _model_instance = None # Class-level singleton
    _tokenizer_instance = None

    def __init__(self, model_name: str = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
        self.model_name = model_name
        self.logger = logging.getLogger("mesh")

    @property
    def model_and_tokenizer(self):
        if SemanticSimilarityEngine._model_instance is None:
            try:
                from transformers import AutoTokenizer, AutoModel
                self.logger.info(f"Loading HF model: {self.model_name}...")
                SemanticSimilarityEngine._tokenizer_instance = AutoTokenizer.from_pretrained(self.model_name)
                SemanticSimilarityEngine._model_instance = AutoModel.from_pretrained(self.model_name)
                # Move to eval mode
                SemanticSimilarityEngine._model_instance.eval()
                self.logger.info("HF model loaded successfully.")
            except Exception as e:
                self.logger.error(f"CRITICAL: Failed to load HF model: {str(e)}")
                return None, None
        return SemanticSimilarityEngine._model_instance, SemanticSimilarityEngine._tokenizer_instance

    def _mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0] # First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        return sum_embeddings / sum_mask

    async def calculate_similarity(self, title1: str, title2: str) -> float:
        model, tokenizer = self.model_and_tokenizer
        if model is None:
            self.logger.warning("HF model unavailable. Falling back to 0.0 similarity.")
            return 0.0
            
        try:
            # Tokenize sentences
            encoded_input = tokenizer([title1, title2], padding=True, truncation=True, return_tensors='pt')
            
            # Compute token embeddings
            with torch.no_grad():
                model_output = model(**encoded_input)
                
            # Perform pooling
            sentence_embeddings = self._mean_pooling(model_output, encoded_input['attention_mask'])
            
            # Normalize embeddings
            sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
            
            # Compute cosine similarity
            cosine_score = (sentence_embeddings[0] @ sentence_embeddings[1].T).item()
            return float(cosine_score)
        except Exception as e:
            self.logger.error(f"Semantic similarity calculation failed: {str(e)}")
            return 0.0

    def encode(self, text: str):
        """Encode a single title into a numpy embedding vector for FAISS."""
        model, tokenizer = self.model_and_tokenizer
        if model is None:
            return None
        try:
            import numpy as np
            encoded_input = tokenizer([text], padding=True, truncation=True, return_tensors='pt')
            with torch.no_grad():
                model_output = model(**encoded_input)
            sentence_embeddings = self._mean_pooling(model_output, encoded_input['attention_mask'])
            sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
            return sentence_embeddings[0].numpy().astype('float32')
        except Exception as e:
            self.logger.error(f"Encoding failed: {e}")
            return None

    def encode_batch(self, texts: list, batch_size: int = 32):
        """Encode a batch of titles into numpy embedding vectors for FAISS."""
        model, tokenizer = self.model_and_tokenizer
        if model is None:
            return None
        try:
            import numpy as np
            all_embeddings = []
            
            # Process in batches to avoid OOM
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                encoded_input = tokenizer(batch_texts, padding=True, truncation=True, return_tensors='pt', max_length=64)
                
                with torch.no_grad():
                    model_output = model(**encoded_input)
                    
                sentence_embeddings = self._mean_pooling(model_output, encoded_input['attention_mask'])
                sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
                all_embeddings.append(sentence_embeddings.numpy().astype('float32'))
                
            return np.vstack(all_embeddings)
        except Exception as e:
            self.logger.error(f"Batch encoding failed: {e}")
            return None
