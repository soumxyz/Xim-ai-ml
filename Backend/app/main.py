import logging
import time
import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import verification_routes, submission_routes, health_routes
from app.monitoring.structured_logger import setup_logging
from app.retrieval.ann_vector_search import ANNVectorSearch
from app.retrieval.inverted_token_index import InvertedTokenIndex
from app.persistence.title_repository import TitleRepository

app = FastAPI(
    title="Metrixa Compliance Core",
    description="Advanced title compliance and verification engine (Lexical Mode)",
    version="2.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store indexes in app.state for dependency injection
# We keep ANNVectorSearch instance for compatibility but it will remain empty/unused in Lexical Mode
app.state.ann_index = ANNVectorSearch() 
app.state.token_index = InvertedTokenIndex()
app.state.sbert_available = False # Explicitly False to signal Lexical fallback

@app.on_event("startup")
async def startup_event():
    setup_logging()
    logger = logging.getLogger("metrixa")
    logger.info("=== Metrixa Compliance Core Startup (Lexical Mode) ===")
    
    start_time = time.time()
    
    # 1. Load titles from JSON dataset
    repo = TitleRepository()
    titles = await repo.get_all_titles()
    
    if not titles:
        logger.warning("No titles found. System will operate in empty-index mode.")
        return
    
    logger.info(f"Loaded {len(titles)} titles for indexing.")
    
    # 2. Build Inverted Token Index (Very fast)
    app.state.token_index.build_index(titles)
    logger.info(f"Inverted token index built with {len(titles)} titles.")
    
    elapsed = time.time() - start_time
    logger.info(f"=== Startup complete in {elapsed:.2f}s (Stable Lexical Mode) ===")

# Include Routers
app.include_router(verification_routes.router, prefix="/api/v1/verify", tags=["Verification"])
app.include_router(submission_routes.router, prefix="/api/v1/submit", tags=["Submission"])
app.include_router(health_routes.router, prefix="/health", tags=["Health"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Metrixa Compliance Core API (Lexical Mode)",
        "version": "2.1.0",
        "mode": "lexical",
        "stable": True,
        "indexed_titles": len(app.state.token_index.titles_map)
    }
