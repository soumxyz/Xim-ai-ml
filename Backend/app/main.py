import logging
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import verification_routes, submission_routes, health_routes
from app.monitoring.structured_logger import setup_logging
from app.retrieval.ann_vector_search import ANNVectorSearch
from app.retrieval.inverted_token_index import InvertedTokenIndex
from app.persistence.title_repository import TitleRepository
from app.intelligence.semantic_similarity_engine import SemanticSimilarityEngine

app = FastAPI(
    title="Metrixa Compliance Core",
    description="Advanced title compliance and verification engine",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store indexes in app.state for dependency injection (no circular imports)
app.state.ann_index = ANNVectorSearch()
app.state.token_index = InvertedTokenIndex()
app.state.sbert_available = False  # Set to True after successful SBERT startup

@app.on_event("startup")
async def startup_event():
    setup_logging()
    logger = logging.getLogger("metrixa")
    logger.info("=== Metrixa Compliance Core Startup ===")
    
    start_time = time.time()
    
    # 1. Load all titles from CSV dataset
    repo = TitleRepository()
    titles = await repo.get_all_titles()
    
    if not titles:
        logger.warning("No titles found. System will operate in empty-index mode.")
        return
    
    logger.info(f"Loaded {len(titles)} titles from dataset.")
    
    # 2. Generate SBERT embeddings (with segfault-safe subprocess pre-check)
    faiss_ready = False
    try:
        import subprocess, sys, os
        
        # Use env var to skip SBERT entirely on known-broken environments
        skip_sbert = os.environ.get("METRIXA_SKIP_SBERT", "0") == "1"
        
        if skip_sbert:
            logger.warning("METRIXA_SKIP_SBERT=1 detected. Skipping SBERT/FAISS indexing.")
        else:
            # Subprocess pre-check: does `import sentence_transformers` survive?
            check = subprocess.run(
                [sys.executable, "-c", "import sentence_transformers; print('OK')"],
                capture_output=True, text=True, timeout=30
            )
            
            if check.returncode == 0 and "OK" in check.stdout:
                sbert = SemanticSimilarityEngine()
                title_texts = [t['title'] for t in titles]
                
                logger.info(f"Generating SBERT embeddings for {len(title_texts)} titles...")
                embeddings = sbert.encode_batch(title_texts)
                
                if embeddings is not None:
                    for i, title_obj in enumerate(titles):
                        title_obj['embedding'] = embeddings[i].tolist()
                    
                    app.state.ann_index.build_index(embeddings.tolist(), titles)
                    logger.info(f"FAISS HNSW index built with {len(embeddings)} vectors.")
                    faiss_ready = True
                    app.state.sbert_available = True
                else:
                    logger.warning("SBERT returned None embeddings.")
            else:
                logger.warning(f"SBERT pre-check FAILED (likely segfault). Skipping FAISS. stderr: {check.stderr[:200]}")
    except Exception as e:
        logger.error(f"Startup SBERT/FAISS indexing failed: {e}")
    
    if not faiss_ready:
        logger.info("Running in RULE-ONLY + TOKEN-INDEX mode (FAISS disabled).")
    
    # 4. Build Inverted Token Index
    app.state.token_index.build_index(titles)
    logger.info(f"Inverted token index built with {len(titles)} titles.")
    
    elapsed = time.time() - start_time
    logger.info(f"=== Startup complete in {elapsed:.2f}s ===")

# Include Routers
app.include_router(verification_routes.router, prefix="/api/v1/verify", tags=["Verification"])
app.include_router(submission_routes.router, prefix="/api/v1/submit", tags=["Submission"])
app.include_router(health_routes.router, prefix="/health", tags=["Health"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Metrixa Compliance Core API",
        "version": "2.0.0",
        "indexed_titles": app.state.ann_index.index.ntotal if hasattr(app.state.ann_index.index, 'ntotal') else 0
    }
