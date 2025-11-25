from db.sessions import SessionLocal
from Controllers.transcription_controller import process_transcription_job


def transcription_job(transcription_id: str) -> None:
    db = SessionLocal()
    try:
        process_transcription_job(db, transcription_id)
    finally:
        db.close()

