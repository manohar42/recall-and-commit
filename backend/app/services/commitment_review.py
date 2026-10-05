from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import Conversation, Utterance
from app.models_commitments import Commitment


def _as_utc(value: datetime) -> datetime:
    """Treat naive database datetimes as UTC; normalize aware ones to UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _due_group(item: Commitment, now: datetime, soon_days: int) -> str:
    if item.status == "done":
        return "done"
    if item.status == "cancelled":
        return "cancelled"
    if item.due_at is None:
        return "undated"

    due = _as_utc(item.due_at)
    if due < now:
        return "overdue"
    if due <= now + timedelta(days=soon_days):
        return "soon"
    return "later"


def _item_to_dict(db: Session, item: Commitment, now: datetime, soon_days: int) -> dict:
    utterance = db.get(Utterance, item.utterance_id)
    conversation = db.get(Conversation, item.conversation_id)

    source = None
    if utterance is not None and conversation is not None:
        source = {
            "conversation_id": conversation.id,
            "conversation_title": conversation.title,
            "utterance_id": utterance.id,
            "sequence": utterance.sequence,
            "speaker": utterance.speaker,
            "text": utterance.text,
        }

    return {
        "id": item.id,
        "candidate_id": item.candidate_id,
        "conversation_id": item.conversation_id,
        "utterance_id": item.utterance_id,
        "action_text": item.action_text,
        "counterparty": item.counterparty,
        "due_text": item.due_text,
        "due_at": item.due_at,
        "status": item.status,
        "completed_at": item.completed_at,
        "source": source,
        "due_group": _due_group(item, now, soon_days),
    }


def list_commitments(
    db: Session,
    status: str | None = None,
    due: str | None = None,
    limit: int = 100,
) -> list[dict]:
    now = datetime.now(timezone.utc)
    query = db.query(Commitment)

    if status:
        query = query.filter(Commitment.status == status)

    items = query.order_by(Commitment.id.desc()).limit(limit).all()
    results = [_item_to_dict(db, item, now, 7) for item in items]

    if due:
        if due not in {"overdue", "soon", "undated", "later"}:
            raise ValueError("due must be overdue, soon, undated, or later")
        results = [row for row in results if row["due_group"] == due]

    # Dated open items first by date; undated items last.
    results.sort(
        key=lambda row: (
            row["due_at"] is None,
            _as_utc(row["due_at"]) if row["due_at"] is not None else datetime.max.replace(tzinfo=timezone.utc),
            row["id"],
        )
    )
    return results


def get_review_summary(
    db: Session,
    soon_days: int = 7,
    completed_days: int = 7,
) -> dict:
    now = datetime.now(timezone.utc)
    items = db.query(Commitment).all()
    mapped = [_item_to_dict(db, item, now, soon_days) for item in items]

    completed_after = now - timedelta(days=completed_days)
    return {
        "overdue": [row for row in mapped if row["due_group"] == "overdue"],
        "due_soon": [row for row in mapped if row["due_group"] == "soon"],
        "undated": [row for row in mapped if row["due_group"] == "undated"],
        "recently_completed": [
            row for row in mapped
            if row["status"] == "done"
            and row["completed_at"] is not None
            and _as_utc(row["completed_at"]) >= completed_after
        ],
    }


def patch_commitment(db: Session, commitment_id: int, changes: dict) -> dict | None:
    item = db.get(Commitment, commitment_id)
    if item is None:
        return None

    allowed = {"action_text", "counterparty", "due_text", "due_at", "status"}
    for field, value in changes.items():
        if field not in allowed:
            continue
        if field == "action_text" and value is not None:
            value = value.strip()
            if not value:
                raise ValueError("action_text cannot be blank")
        setattr(item, field, value)

    if item.status == "done":
        item.completed_at = datetime.now(timezone.utc)
    elif item.status == "open":
        item.completed_at = None

    db.add(item)
    try:
        db.commit()
        db.refresh(item)
    except Exception:
        db.rollback()
        raise

    return _item_to_dict(
        db,
        item,
        datetime.now(timezone.utc),
        7,
    )