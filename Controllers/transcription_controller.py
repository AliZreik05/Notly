import openai
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from db.models import Transcription as TranscriptionModel
from schemas.transcription_schema import TranscriptionCreate, TranscriptionStatus
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

async def create_transcription(db: Session, file: UploadFile, title: str):
    """
    Creates a transcription for the given audio file.

    Args:
        db (Session): The database session.
        file (UploadFile): The audio file to transcribe.
        title (str): The title of the transcription.

    Returns:
        TranscriptionModel: The created transcription.
    """
    if not file.content_type in ["audio/mpeg", "audio/wav", "audio/x-m4a"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only .mp3, .wav, and .m4a are supported.",
        )

    transcription_data = TranscriptionCreate(title=title)
    db_transcription = TranscriptionModel(**transcription_data.dict())
    db.add(db_transcription)
    db.commit()
    db.refresh(db_transcription)

    try:
        # Save the uploaded file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Transcribe the audio file
        with open(file_path, "rb") as audio_file:
            transcription = openai.Audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )

        # Update the transcription object
        db_transcription.text = transcription.text
        db_transcription.duration = transcription.duration
        db_transcription.word_count = len(transcription.text.split())
        db_transcription.status = TranscriptionStatus.COMPLETED

    except Exception as e:
        db_transcription.status = TranscriptionStatus.FAILED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transcribe audio: {str(e)}",
        )
    finally:
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

    db.commit()
    db.refresh(db_transcription)
    return db_transcription