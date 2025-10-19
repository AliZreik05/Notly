from fastapi import APIRouter, HTTPException
from Schemas.NoteSummarizer import SummarizeNoteRequest, SummarizeNoteResponse
from Controllers.NoteSummarizer import summarize_text

router = APIRouter(prefix="/notessummarizer", tags=["Notes"])

@router.post("/summarize", response_model=SummarizeNoteResponse)
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
