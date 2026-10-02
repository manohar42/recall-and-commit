import re

from sqlalchemy import text
from sqlalchemy.orm import Session, selectinload

from app.models import Conversation

def rebuild_recall_index(db: Session) -> int:
    """Replace the index contents using the currently stored conversations."""
    db.execute(text("""
        CREATE VIRTUAL TABLE IF NOT EXISTS recall_fts USING fts5(
            conversation_id UNINDEXED,
            conversation_title UNINDEXED,
            sequence_start UNINDEXED,
            sequence_end UNINDEXED,
            excerpt
        )
    """))
    db.execute(text("DELETE FROM recall_fts"))

    conversations = (
        db.query(Conversation)
        .options(selectinload(Conversation.utterances))
        .all()
    )

    inserted = 0

    for conversation in conversations:
        utterances = sorted(
            conversation.utterances,
            key=lambda utterance: utterance.sequence,
        )

        for start in range(0, len(utterances), 4):
            group = utterances[start : start + 4]
            if not group:
                continue

            excerpt = "\n".join(
                f"{utterance.speaker}: {utterance.text}"
                for utterance in group
            )

            db.execute(
                text("""
                    INSERT INTO recall_fts (
                        conversation_id,
                        conversation_title,
                        sequence_start,
                        sequence_end,
                        excerpt
                    )
                    VALUES (
                        :conversation_id,
                        :conversation_title,
                        :sequence_start,
                        :sequence_end,
                        :excerpt
                    )
                """),
                {
                    "conversation_id": conversation.id,
                    "conversation_title": conversation.title,
                    "sequence_start": group[0].sequence,
                    "sequence_end": group[-1].sequence,
                    "excerpt": excerpt,
                },
            )
            inserted += 1

    db.commit()
    return inserted

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "did", "do",
    "does", "for", "from", "had", "has", "have", "how", "i", "if", "in",
    "is", "it", "its", "me", "my", "of", "on", "or", "our", "should",
    "so", "than", "that", "the", "their", "then", "there", "this", "to",
    "was", "we", "were", "what", "when", "where", "which", "who", "why",
    "will", "with", "would", "you", "your",
}


def _make_fts_query(question: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", question.lower())
    keywords = [w for w in words if w not in STOP_WORDS and len(w) > 1]
    if not keywords:
        return ""
    return " OR ".join(f'"{word}"' for word in dict.fromkeys(keywords))

def search_recall(db: Session, question: str, limit: int) -> list[dict]:
    query = _make_fts_query(question)
    if not query:
        return []

    rows = db.execute(
        text("""
            SELECT
                conversation_id,
                conversation_title,
                sequence_start,
                sequence_end,
                excerpt,
                bm25(recall_fts) AS score
            FROM recall_fts
            WHERE recall_fts MATCH :query
            ORDER BY score
            LIMIT :limit
        """),
        {"query": query, "limit": limit},
    ).mappings()

    return [dict(row) for row in rows]