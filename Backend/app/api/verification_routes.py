from fastapi import APIRouter, Request
from app.api.request_models import VerificationRequest, ComplianceResult
from app.orchestration.mesh_orchestrator import MeshOrchestrator

router = APIRouter()

@router.post("/", response_model=ComplianceResult)
async def verify_title(request: VerificationRequest, req: Request):
    # Get shared indexes and flags from app state (injected at startup)
    ann_index = getattr(req.app.state, 'ann_index', None)
    token_index = getattr(req.app.state, 'token_index', None)
    sbert_available = getattr(req.app.state, 'sbert_available', False)
    
    orchestrator = MeshOrchestrator(
        ann_index=ann_index,
        token_index=token_index,
        sbert_available=sbert_available
    )
    result = await orchestrator.verify(request.title)
    return result
