from pydantic import BaseModel, Field, field_validator
from datetime import datetime

# class Conversations(BaseModel):

#     id : str
#     source_type : str
#     external_id : str
#     title: str
#     started_at: datetime
#     ended_at: datetime
#     participants_json : list[str]
#     content_hash : str
#     imported_at : str
#     updated_at : datetime
#     deleted_at : datetime



# class Utterences(BaseModel):

#     id : str
#     Conversation_id : str
#     sequence : int
#     speaker: str
#     occured_at : str
#     text : str

class SampleUtteranceInput(BaseModel):

    sequence: int = Field(gt=0)
    speaker: str = Field(min_length=1)
    occured_at : datetime | None = None
    text: str = Field(min_length=1)

    @field_validator("text")
    @classmethod
    def strip_text(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError("utterance text cannot be empty.")

class SampleConversationInput(BaseModel):

    external_id : str = Field(gt=0)
    title : str = Field(min_length=1)
    started_at : datetime
    ended_at : datetime
    participants : list[str] = Field(min_length=1)
    utterances : list[SampleUtteranceInput] = Field(min_length=1)

    @field_validator("utterances")
    @classmethod
    def unique_sequences(cls,v:list[SampleUtteranceInput]):

        sequences = [u.sequence for u in v]
        if len(sequences) != len(set(sequences)):
            raise ValueError("utterance sequence numbers must be unique.")

        return v

class SampleImportPayload(BaseModel):

    schema_version : str
    source : str
    conversations: list[SampleConversationInput]

class ImportSummaryPayload(BaseModel):

    status : str
    source : str
    conversation_received : int
    conversation_created: int

class UtteranceResponse(BaseModel):
    sequence: int
    speaker : str
    occured_at: datetime | None
    text: str

class ConversationListTime(BaseModel):
    id: int
    external_id : str
    source_type : str
    title : str
    started_at : datetime
    participants : list[str]
    utterance_count : int

class ConversationDetail(BaseModel):
    id : int
    external_id : str
    source_type : str
    title : str
    started_at : datetime
    ended_at : datetime | None
    participants : list[str]
    utterances : list[UtteranceResponse]
    