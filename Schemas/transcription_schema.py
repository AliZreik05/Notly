from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import enum


class TranscriptionStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TranscriptionUploadResponse(BaseModel):
    id: str = Field(..., description="Public identifier for the transcription job")
    status: TranscriptionStatus


class TranscriptionHistoryItem(BaseModel):
    id: str
    course: Optional[str] = None
    word_count: Optional[int] = None
    created_at: datetime
    duration: Optional[str] = Field(
        default=None, description="HH:MM:SS formatted audio duration"
    )
    status: TranscriptionStatus


class TranscriptionDetail(BaseModel):
    id: str
    title: str
    course_name: Optional[str] = None
    audio_url: str
    transcript_text: Optional[str] = None
    summary_text: Optional[str] = None
    duration_seconds: Optional[int] = None
    duration: Optional[str] = None
    word_count: Optional[int] = None
    status: TranscriptionStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
