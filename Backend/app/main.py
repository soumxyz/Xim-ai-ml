import logging
from fastapi import FastAPI
from app.api import verification_routes, submission_routes, health_routes
from app.monitoring.structured_logger import setup_logging
from app.retrieval.ann_vector_search import ANNVectorSearch
from app.retrieval.inverted_token_index import InvertedTokenIndex
from app.persistence.title_repository import TitleRepository

app = FastAPI(
    title="Metrixa Compliance Core",
    description="Advanced title compliance and verification engine",
    version="1.0.0"
)

# Global instances for in-memory indexes
ann_index = ANNVectorSearch()
token_index = InvertedTokenIndex()

@app.on_event("startup")
async def startup_event():
    setup_logging()
    logger = logging.getLogger("metrixa")
    logger.info("Initializing system indexes...")
    
    # 1. Load all titles from DB
    repo = TitleRepository()
    titles = await repo.get_all_titles() # Should return list of dicts with id, title, normalized_title, embedding
    
    if titles:
        # 2. Build FAISS index
        embeddings = [t['embedding'] for t in titles if 'embedding' in t]
        if embeddings:
            ann_index.build_index(embeddings, titles)
            logger.info(f"FAISS index built with {len(embeddings)} titles.")
        
        # 3. Build Inverted Token Index
        token_index.build_index(titles)
        logger.info("Inverted token index built.")
    else:
        logger.warning("No titles found in DB to index.")

# Include Routers
app.include_router(verification_routes.router, prefix="/api/v1/verify", tags=["Verification"])
app.include_router(submission_routes.router, prefix="/api/v1/submit", tags=["Submission"])
app.include_router(health_routes.router, prefix="/health", tags=["Health"])

@app.get("/")
async def root():
    return {"message": "Welcome to Metrixa Compliance Core API"}
