from pydantic import BaseModel, Field


class RecallRequest(BaseModel):
    question : str =  Field(min_length=1, max_length=500)

    limit: int = Field(default=5, ge=1, le = 20)

class RecallEvidence(BaseModel):

    conversation_id : int
    conversation_title : str
    sequence_start : int
    sequence_end : int
    excerpt : str
    score: float

class RecallResponse(BaseModel):

    question : str
    insufficient_evidence : bool
    results : list[RecallEvidence]

