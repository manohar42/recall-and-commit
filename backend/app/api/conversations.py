import json

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session, selectinload
from app.storage import get_db
from app.schemas.imports import ConversationDetail, ConversationListItem, UtteranceResponse
from app.models import Conversation


router = APIRouter(prefix="/api/conversations", tags=["conversations"])

@router.get("",response_model=list[ConversationListItem])
async def list_conversations(db: Session = Depends(get_db)) -> list[ConversationListItem]:
    conversations = db.query(Conversation).all()

    return [
        ConversationListItem(
            id=c.id,
            external_id=c.external_id,
            source_type=c.source_type,
            title=c.title,
            started_at=c.started_at,
            participants=json.loads(c.participants_json),
            utterance_count=len(c.utterances),
        )
        for c in conversations
    ]

@router.get(
    "/{conversation_id}",
    response_model=ConversationDetail,
)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
) -> ConversationDetail:
    conversation = (
        db.query(Conversation)
        .options(selectinload(Conversation.utterances))
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return ConversationDetail(
        id=conversation.id,
        external_id=conversation.external_id,
        source_type=conversation.source_type,
        title=conversation.title,
        started_at=conversation.started_at,
        ended_at=conversation.ended_at,
        participants=json.loads(conversation.participants_json),
        utterances=[
            UtteranceResponse(
                sequence=u.sequence,
                speaker=u.speaker,
                occurred_at=u.occurred_at,
                text=u.text,
            )
            for u in sorted(
                conversation.utterances,
                key=lambda utterance: utterance.sequence,
            )
        ],
    )


