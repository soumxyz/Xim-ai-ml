from fastapi import APIRouter
from app.api.request_models import TitleSubmission

router = APIRouter()

@router.post("/")
async def submit_title(submission: TitleSubmission):
    return {"message": "Title submitted successfully", "submission_id": "12345"}
