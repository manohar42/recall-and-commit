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


class CommitmentUpdate(BaseModel):
    status: Literal["open", "done", "cancelled"]


class DetectSummary(BaseModel):
    scanned_utterances: int
    new_candidates: int
    skipped_existing: int