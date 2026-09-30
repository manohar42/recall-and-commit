import hashlib
import json

from sqlalchemy.orm import Session

from app.models import Conversation, Utterance
from app.schemas.imports import SampleConversationInput, SampleImportPayload, ImportSummaryResponse


def _content_hash(conv: SampleConversationInput) -> str:
    payload = conv.model_dump_json()
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def import_sample_payload(db: Session, payload: SampleImportPayload) -> ImportSummaryResponse:
    created = 0
    updated = 0
    skipped = 0
    utterances_created = 0

    for conv_input in payload.conversations:
        new_hash = _content_hash(conv_input)

        existing = (
            db.query(Conversation)
            .filter(
                Conversation.source_type == payload.source,
                Conversation.external_id == conv_input.external_id,
            )
            .first()
        )

        if existing and existing.content_hash == new_hash:
            skipped += 1
            continue

        if existing:
            db.query(Utterance).filter(Utterance.conversation_id == existing.id).delete()
            existing.title = conv_input.title
            existing.started_at = conv_input.started_at
            existing.ended_at = conv_input.ended_at
            existing.participants_json = json.dumps(conv_input.participants)
            existing.content_hash = new_hash
            conversation = existing
            updated += 1
        else:
            conversation = Conversation(
                source_type=payload.source,
                external_id=conv_input.external_id,
                title=conv_input.title,
                started_at=conv_input.started_at,
                ended_at=conv_input.ended_at,
                participants_json=json.dumps(conv_input.participants),
                content_hash=new_hash,
            )
            db.add(conversation)
            db.flush()
            created += 1

        for u in conv_input.utterances:
            db.add(
                Utterance(
                    conversation_id=conversation.id,
                    sequence=u.sequence,
                    speaker=u.speaker,
                    occurred_at=u.occurred_at,
                    text=u.text,
                )
            )
            utterances_created += 1

    db.commit()

    return ImportSummaryResponse(
        status="completed",
        source=payload.source,
        conversations_received=len(payload.conversations),
        conversations_created=created,
        conversations_updated=updated,
        conversations_skipped=skipped,
        utterances_created=utterances_created,
    )