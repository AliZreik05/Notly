from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from db.sessions import get_db
from Controllers.transcription_controller import create_transcription
from Schemas.transcription_schema import TranscriptionResponse, Transcription

router = APIRouter(prefix="/transcribe", tags=["Transcription"])

@router.post("/", response_model=TranscriptionResponse, status_code=status.HTTP_201_CREATED)
async def transcribe_audio(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Uploads an audio file and transcribes it using OpenAI Whisper.

    Args:
        title (str): The title of the transcription.
        file (UploadFile): The audio file to transcribe (.mp3, .wav, .m4a).
        db (Session): The database session.

    Returns:
        TranscriptionResponse: The status of the transcription and the stored data.
    """
    transcription = await create_transcription(db=db, file=file, title=title)
    return {"status": "success", "transcription": transcription}