from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class SampleUtteranceInput(BaseModel):
    sequence: int = Field(gt=0)
    speaker: str = Field(min_length=1)
    occurred_at: datetime | None = None
    text: str = Field(min_length=1)

    @field_validator("text")
    @classmethod
    def strip_text(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("utterance text cannot be empty")
        return v


class SampleConversationInput(BaseModel):
    external_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    started_at: datetime
    ended_at: datetime | None = None
    participants: list[str] = Field(min_length=1)
    utterances: list[SampleUtteranceInput] = Field(min_length=1)

    @field_validator("utterances")
    @classmethod
    def unique_sequences(cls, v: list[SampleUtteranceInput]):
        sequences = [u.sequence for u in v]
        if len(sequences) != len(set(sequences)):
            raise ValueError("utterance sequence numbers must be unique")
        return v


class SampleImportPayload(BaseModel):
    schema_version: str
    source: str
    conversations: list[SampleConversationInput]


class ImportSummaryResponse(BaseModel):
    status: str
    source: str
    conversations_received: int
    conversations_created: int
    conversations_updated: int
    conversations_skipped: int
    utterances_created: int


class UtteranceResponse(BaseModel):
    sequence: int
    speaker: str
    occurred_at: datetime | None
    text: str


class ConversationListItem(BaseModel):
    id: int
    external_id: str
    source_type: str
    title: str
    started_at: datetime
    participants: list[str]
    utterance_count: int


class ConversationDetail(BaseModel):
    id: int
    external_id: str
    source_type: str
    title: str
    started_at: datetime
    ended_at: datetime | None
    participants: list[str]
    utterances: list[UtteranceResponse]