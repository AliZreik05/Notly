from pydantic import BaseModel, Field
from typing import Optional, List

class SummarizeNoteRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Raw note text to summarize")
    max_sentences: int = Field(3, ge=1, le=10, description="Max sentences in summary")

class SummarizeNoteResponse(BaseModel):
    summary: str
    sentences_used: List[str]
    original_char_len: int
    summary_char_len: int
    compression_ratio: float