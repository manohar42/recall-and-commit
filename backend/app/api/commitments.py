from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models_commitments import Commitment, CommitmentCandidate
from app.schemas.commitments import (
    ApproveRequest, CandidateOut, CommitmentOut, CommitmentUpdate, DetectSummary,
)
from app.services import commitments as svc
from app.storage import get_db

router = APIRouter(prefix="/api/commitments", tags=["Commitments"])


def _raise(exc: svc.ReviewError):
    raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.post("/detect", response_model=DetectSummary)
def detect(db: Session = Depends(get_db)):
    return svc.detect_all(db)


@router.get("/candidates", response_model=list[CandidateOut])
def list_candidates(
    status: str = Query(default="pending", pattern="^(pending|approved|rejected)$"),
    db: Session = Depends(get_db),
):
    return (
        db.query(CommitmentCandidate)
        .filter(CommitmentCandidate.status == status)
        .order_by(CommitmentCandidate.id)
        .all()
    )


@router.post("/candidates/{candidate_id}/approve", response_model=CommitmentOut)
def approve(candidate_id: int, body: ApproveRequest | None = None, db: Session = Depends(get_db)):
    edits = body.model_dump() if body else {}
    try:
        return svc.approve_candidate(db, candidate_id, edits)
    except svc.ReviewError as exc:
        _raise(exc)


@router.post("/candidates/{candidate_id}/reject", response_model=CandidateOut)
def reject(candidate_id: int, db: Session = Depends(get_db)):
    try:
        return svc.reject_candidate(db, candidate_id)
    except svc.ReviewError as exc:
        _raise(exc)


@router.get("", response_model=list[CommitmentOut])
def list_ledger(
    status: str | None = Query(default=None, pattern="^(open|done|cancelled)$"),
    db: Session = Depends(get_db),
):
    q = db.query(Commitment)
    if status:
        q = q.filter(Commitment.status == status)
    return q.order_by(Commitment.due_at.is_(None), Commitment.due_at, Commitment.id).all()


@router.patch("/{commitment_id}", response_model=CommitmentOut)
def update(commitment_id: int, body: CommitmentUpdate, db: Session = Depends(get_db)):
    try:
        return svc.update_commitment_status(db, commitment_id, body.status)
    except svc.ReviewError as exc:
        _raise(exc)