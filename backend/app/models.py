from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.storage import Base


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (UniqueConstraint("source_type", "external_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    source_type: Mapped[str] = mapped_column(String(20))
    external_id: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(255))
    started_at: Mapped[datetime]
    ended_at: Mapped[datetime | None]
    participants_json: Mapped[str] = mapped_column(Text, default="[]")
    content_hash: Mapped[str] = mapped_column(String(64))
    imported_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    utterances: Mapped[list["Utterance"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Utterance.sequence",
    )


class Utterance(Base):
    __tablename__ = "utterances"
    __table_args__ = (UniqueConstraint("conversation_id", "sequence"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    sequence: Mapped[int]
    speaker: Mapped[str] = mapped_column(String(100))
    occurred_at: Mapped[datetime | None]
    text: Mapped[str] = mapped_column(Text)

    conversation: Mapped["Conversation"] = relationship(back_populates="utterances")