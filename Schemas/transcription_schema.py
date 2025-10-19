from pydantic import BaseModel, Field
from typing import Optional
import enum

class TranscriptionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class TranscriptionBase(BaseModel):
    title: str
    duration: Optional[float] = None
    word_count: Optional[int] = None
    status: TranscriptionStatus = TranscriptionStatus.PENDING

class TranscriptionCreate(TranscriptionBase):
    pass

class Transcription(TranscriptionBase):
    id: int
    text: str

    class Config:
        orm_mode = True

class TranscriptionResponse(BaseModel):
    status: str
    transcription: Optional[Transcription] = None
