from pydantic import BaseModel, Field
from datetime import datetime

class Conversations(BaseModel):

    id : str
    source_type : str
    external_id : str
    title: str
    started_at: datetime
    ended_at: datetime
    participants_json : list[str]
    content_hash : str
    imported_at : str
    updated_at : datetime
    deleted_at : datetime



class Utterences(BaseModel):

    id : str
    Conversation_id : str
    sequence : int
    speaker: str
    occured_at : str
    text : str