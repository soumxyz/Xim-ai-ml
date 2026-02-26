from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class VerificationRequest(BaseModel):
    title: str = Field(..., example="Sunrise Chronicle")
    context: Optional[str] = None

class ConflictDetail(BaseModel):
    title: str
    conflict_type: str # 'Semantic', 'Phonetic', 'Lexical', 'Token'
    similarity_score: float
    highlighted_text: str # From Bionic layer

class ComplianceResult(BaseModel):
    is_compliant: bool
    verification_probability: float
    decision: str
    explanation: str
    conflicts: List[ConflictDetail]
    scores: Dict[str, float]
    metadata: Optional[Dict] = None

class TitleSubmission(BaseModel):
    title: str
    metadata: Optional[dict] = None
