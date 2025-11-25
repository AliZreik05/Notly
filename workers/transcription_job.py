from db.sessions import SessionLocal



def transcription_job(transcription_id: str) -> None:
    # Import the controller function at runtime to avoid a circular
    # import between Controllers.transcription_controller and this module
    # during application startup / import time.
    from Controllers.transcription_controller import process_transcription_job

    db = SessionLocal()
    try:
        process_transcription_job(db, transcription_id)
    finally:
        db.close()

