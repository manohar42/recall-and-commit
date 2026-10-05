from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CandidateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    utterance_id: int
    utterance_sequence: int
    speaker: str | None
    source_text: str
    action_text: str
    counterparty: str | None
    due_text: str | None
    due_at: datetime | None
    confidence: float
    status: str


class ApproveRequest(BaseModel):
    action_text: str | None = Field(default=None, min_length=1, max_length=500)
    counterparty: str | None = None
    due_text: str | None = None
    due_at: datetime | None = None

class SourceOut(BaseModel):
    conversation_id : int
    conversation_title : str
    utterance_id: int
    sequence: int
    speaker: str| None
    text : str

class CommitmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_id: int
    conversation_id: int
    utterance_id: int
    action_text: str
    counterparty: str | None
    due_text: str | None
    due_at: datetime | None
    status: str
    completed_at: datetime | None
    source : SourceOut | None
    due_group : Literal["overdue","soon","undated","later","done","cancelled"]


class CommitmentUpdate(BaseModel):
    status: Literal["open", "done", "cancelled"]


class DetectSummary(BaseModel):
    scanned_utterances: int
    new_candidates: int
    skipped_existing: int


class CommitmentPatch(BaseModel):
    action_text: str | None = Field(default=None, min_length=1, max_length=500)
    counterparty: str | None = Field(default=None, max_length=200)
    due_text: str | None = Field(default=None, max_length=200)
    due_at: datetime | None = None
    status: Literal["open", "done", "cancelled"] | None = None

class ReviewSummary(BaseModel):
    overdue: list[CommitmentOut]
    due_soon: list[CommitmentOut]
    undated: list[CommitmentOut]
    recently_completed: list[CommitmentOut]
