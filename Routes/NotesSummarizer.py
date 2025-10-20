from fastapi import APIRouter, HTTPException
from Schemas.NoteSummarizerschema import SummarizeNoteRequest, SummarizeNoteResponse
from Controllers.NoteSummarizer import summarize_text

router = APIRouter(prefix="/summarize", tags=["Notes"])

@router.post("/", response_model=SummarizeNoteResponse)
def summarize_note(payload: SummarizeNoteRequest):
    text = payload.text.strip()
    if len(text) < 10:
        raise HTTPException(status_code=400, detail="Text too short to summarize.")

    summary, sentences_used = summarize_text(text, payload.max_sentences)
    return SummarizeNoteResponse(
        summary=summary,
        sentences_used=sentences_used,
        original_char_len=len(text),
        summary_char_len=len(summary),
        compression_ratio=(len(summary) / max(1, len(text)))
    )

@router.get("/")
def ping_notes():
    return {"message": "NoteSummarizer endpoint is live"}