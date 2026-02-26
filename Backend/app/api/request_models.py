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

class AnalysisDetail(BaseModel):
    lexical_similarity: int
    phonetic_similarity: int
    semantic_similarity: int
    disallowed_word: bool
    periodicity_violation: bool
    combination_violation: bool
    prefix_suffix_violation: bool

class ComplianceResult(BaseModel):
    is_compliant: bool
    verification_probability: float
    decision: str
    explanation: str
    conflicts: List[ConflictDetail]
    scores: Dict[str, float]
    analysis: Optional[AnalysisDetail] = None
    metadata: Optional[Dict] = None

class TitleSubmission(BaseModel):
    title: str
    metadata: Optional[dict] = None
