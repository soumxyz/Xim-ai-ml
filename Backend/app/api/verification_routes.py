from fastapi import APIRouter
from app.api.request_models import VerificationRequest, ComplianceResult
from app.orchestration.metrixa_orchestrator import MetrixaOrchestrator

router = APIRouter()
orchestrator = MetrixaOrchestrator()

@router.post("/", response_model=ComplianceResult)
async def verify_title(request: VerificationRequest):
    return await orchestrator.verify(request.title)
