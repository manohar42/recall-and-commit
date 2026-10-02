from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.recall import RecallRequest, RecallResponse, RecallEvidence
from app.services.recall import search_recall
from app.storage import get_db

router = APIRouter(prefix="/api/recall", tags=["Recall"])


@router.post("", response_model=RecallResponse)
def recall(
    request: RecallRequest,
    db: Session = Depends(get_db),
) -> RecallResponse:
    results = search_recall(
        db,
        question=request.question,
        limit=request.limit,
    )

    evidence = [RecallEvidence(**result) for result in results]

    return RecallResponse(
        question=request.question,
        insufficient_evidence=len(evidence) == 0,
        results=evidence,
    )