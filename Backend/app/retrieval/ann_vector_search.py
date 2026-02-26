import faiss
import numpy as np

class ANNVectorSearch:
    def __init__(self, dimension: int = 384): # Default for MiniLM
        self.dimension = dimension
        # HNSW index for high-speed retrieval
        # M is the number of established connections (16-64 is reasonable)
        self.index = faiss.IndexHNSWFlat(dimension, 32)
        self.index.hnsw.efConstruction = 40
        self.index.hnsw.efSearch = 16
        self.metadata = []

    def build_index(self, embeddings: list, titles: list):
        if not embeddings:
            return
        
        embeddings_np = np.array(embeddings).astype('float32')
        # Re-initialize to clear and reset dimension/parameters
        self.index = faiss.IndexHNSWFlat(self.dimension, 32)
        self.index.add(embeddings_np)
        self.metadata = titles

    async def get_top_candidates(self, query_embedding: np.ndarray, top_k: int = 20):
        if self.index.ntotal == 0:
            return []
        
        query_np = query_embedding.astype('float32').reshape(1, -1)
        distances, indices = self.index.search(query_np, top_k)
        
        candidates = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata):
                candidate = self.metadata[idx].copy()
                candidate['vector_distance'] = float(distances[0][i])
                candidates.append(candidate)
        
        return candidates
