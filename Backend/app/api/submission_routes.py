import logging
from fastapi import APIRouter, Request
from app.api.request_models import TitleSubmission
from app.persistence.title_repository import TitleRepository
from app.intelligence.semantic_similarity_engine import SemanticSimilarityEngine

router = APIRouter()

@router.post("/")
async def submit_title(submission: TitleSubmission, req: Request):
    """
    Accepts a verified title and adds it to the live index.
    Demonstrates the 'Pending Title Re-Index Trigger' flow.
    """
    logger = logging.getLogger("metrixa")
    
    repo = TitleRepository()
    existing = await repo.get_all_titles()
    new_id = max((t["id"] for t in existing), default=0) + 1
    normalized = submission.title.lower().strip()
    
    new_entry = {
        "id": new_id,
        "title": submission.title,
        "normalized_title": normalized
    }
    
    # 1. Add to in-memory cache
    TitleRepository.add_to_cache(new_entry)
    
    # 2. Generate embedding and inject into FAISS index (only if SBERT available)
    ann_index = getattr(req.app.state, 'ann_index', None)
    token_index = getattr(req.app.state, 'token_index', None)
    sbert_available = getattr(req.app.state, 'sbert_available', False)
    
    faiss_updated = False
    if sbert_available and ann_index:
        try:
            sbert = SemanticSimilarityEngine()
            embedding = sbert.encode(submission.title)
            
            if embedding is not None:
                import numpy as np
                new_entry['embedding'] = embedding.tolist()
                ann_index.index.add(np.array([embedding]))
                ann_index.metadata.append(new_entry)
                faiss_updated = True
                logger.info(f"FAISS index updated. New total: {ann_index.index.ntotal}")
        except Exception as e:
            logger.error(f"FAISS injection failed: {e}")
    
    # 3. Update inverted token index (always works)
    if token_index:
        token_index.titles_map[new_id] = new_entry
        for token in set(normalized.split()):
            token_index.index[token].append(new_id)
        logger.info(f"Token index updated with '{submission.title}'")
    
    total_indexed = ann_index.index.ntotal if ann_index and hasattr(ann_index.index, 'ntotal') else len(token_index.titles_map) if token_index else "unknown"
    
    return {
        "message": "Title accepted and indexed successfully",
        "title_id": new_id,
        "title": submission.title,
        "faiss_updated": faiss_updated,
        "indexed_total": total_indexed
    }
