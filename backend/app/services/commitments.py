from datetime import datetime, timezone

from sqlalchemy.orm import Session, selectinload

from app.models import Conversation
from app.models_commitments import Commitment, CommitmentCandidate
from app.services.commitment_detector import detect_commitment, parse_due


class ReviewError(Exception):
    """Raised when a candidate can't be reviewed (missing or already reviewed)."""

    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code


def detect_all(db: Session) -> dict:
    existing = {
        row[0] for row in db.query(CommitmentCandidate.utterance_id).all()
    }
    scanned = created = skipped = 0

    conversations = db.query(Conversation).options(selectinload(Conversation.utterances)).all()
    for conv in conversations:
        utterances = sorted(conv.utterances, key=lambda u: u.sequence)
        for u in utterances:
            scanned += 1
            if u.id in existing:
                skipped += 1
                continue

            others = tuple({x.speaker for x in utterances if x.speaker and x.speaker != u.speaker})
            found = detect_commitment(u.text, others)
            if not found:
                continue

            db.add(CommitmentCandidate(
                conversation_id=conv.id,
                utterance_id=u.id,
                utterance_sequence=u.sequence,
                speaker=u.speaker,
                source_text=u.text,
                action_text=found.action_text,
                counterparty=found.counterparty,
                due_text=found.due_text,
                due_at=parse_due(found.due_text, getattr(conv, "started_at", None)),
                confidence=found.confidence,
                status="pending",
            ))
            existing.add(u.id)
            created += 1

    db.commit()
    return {"scanned_utterances": scanned, "new_candidates": created, "skipped_existing": skipped}


def _get_pending(db: Session, candidate_id: int) -> CommitmentCandidate:
    cand = db.get(CommitmentCandidate, candidate_id)
    if cand is None:
        raise ReviewError("Candidate not found", 404)
    if cand.status != "pending":
        raise ReviewError(f"Candidate already {cand.status}", 409)
    return cand


def approve_candidate(db: Session, candidate_id: int, edits: dict) -> Commitment:
    cand = _get_pending(db, candidate_id)

    for field in ("action_text", "counterparty", "due_text", "due_at"):
        if edits.get(field) is not None:
            setattr(cand, field, edits[field])

    now = datetime.now(timezone.utc)
    cand.status = "approved"
    cand.reviewed_at = now

    commitment = Commitment(
        candidate_id=cand.id,
        conversation_id=cand.conversation_id,
        utterance_id=cand.utterance_id,
        action_text=cand.action_text,
        counterparty=cand.counterparty,
        due_text=cand.due_text,
        due_at=cand.due_at,
        status="open",
    )
    db.add(commitment)
    db.commit()
    db.refresh(commitment)
    return commitment


def reject_candidate(db: Session, candidate_id: int) -> CommitmentCandidate:
    cand = _get_pending(db, candidate_id)
    cand.status = "rejected"
    cand.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(cand)
    return cand


def update_commitment_status(db: Session, commitment_id: int, status: str) -> Commitment:
    item = db.get(Commitment, commitment_id)
    if item is None:
        raise ReviewError("Commitment not found", 404)
    item.status = status
    item.completed_at = datetime.now(timezone.utc) if status == "done" else None
    db.commit()
    db.refresh(item)
    return item