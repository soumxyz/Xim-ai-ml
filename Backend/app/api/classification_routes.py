import logging
from fastapi import APIRouter, Request
from app.api.request_models import ClassificationRequest, ClassificationResult

router = APIRouter()


@router.post("/", response_model=ClassificationResult)
async def classify_article(request: ClassificationRequest, req: Request):
    """
    Classify a news article into one of 33 categories based on
    headline and optional description.

    Uses a TF-IDF + LinearSVC model trained on 209K+ HuffPost articles.
    """
    logger = logging.getLogger("mesh")

    classifier = getattr(req.app.state, "news_classifier", None)
    if classifier is None:
        return ClassificationResult(
            category="UNKNOWN",
            confidence=0.0,
            top_predictions=[],
            model_info={"error": "Classifier not loaded"},
        )

    result = classifier.predict(
        headline=request.headline,
        short_description=request.short_description or "",
    )

    logger.info(
        f"Classified '{request.headline[:50]}...' → {result['category']} "
        f"({result['confidence']:.2%})"
    )

    return ClassificationResult(
        category=result["category"],
        confidence=result["confidence"],
        top_predictions=result["top_predictions"],
        model_info={
            "model_type": "TF-IDF + LinearSVC (CalibratedClassifierCV)",
            "training_samples": 209521,
            "num_categories": 33,
        },
    )
