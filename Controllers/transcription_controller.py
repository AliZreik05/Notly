import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import openai
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from db.models import Transcription as TranscriptionModel, TranscriptionStatus
from Schemas.transcription_schema import TranscriptionHistoryItem, TranscriptionDetail
from services.storage import store_audio_file
from services.queue import transcription_queue
from workers.transcription_job import transcription_job

ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/x-m4a", "audio/mp4", "audio/aac"}
SUMMARY_MODEL = os.getenv("SUMMARY_MODEL", "gpt-4o-mini")
TRANSCRIPTION_MODEL = os.getenv("TRANSCRIPTION_MODEL", "whisper-1")

openai.api_key = os.getenv("OPENAI_API_KEY")


async def create_transcription_request(
    db: Session,
    *,
    user_id: int,
    file: UploadFile,
    title: str,
    course_name: Optional[str],
) -> TranscriptionModel:
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only .mp3, .wav, .m4a, or .aac files are supported.",
        )

    stored_file = await store_audio_file(file, user_id)
    transcription = TranscriptionModel(
        user_id=user_id,
        title=title,
        course_name=course_name,
        audio_url=stored_file.public_url,
        audio_path=str(stored_file.absolute_path),
        status=TranscriptionStatus.PENDING,
    )
    db.add(transcription)
    db.commit()
    db.refresh(transcription)

    transcription_queue.enqueue(transcription_job, transcription_id=transcription.id)
    return transcription


def list_transcriptions_for_history(
    db: Session, *, user_id: int, filter_value: Optional[str]
) -> List[TranscriptionHistoryItem]:
    query = (
        db.query(TranscriptionModel)
        .filter(TranscriptionModel.user_id == user_id)
        .order_by(TranscriptionModel.created_at.desc())
    )
    query = _apply_history_filter(query, filter_value)

    items: List[TranscriptionHistoryItem] = []
    for row in query.all():
        items.append(
            TranscriptionHistoryItem(
                id=row.id,
                course=row.course_name,
                word_count=row.word_count,
                created_at=row.created_at,
                duration=_format_duration(row.duration_seconds),
                status=row.status,
            )
        )
    return items


def get_transcription_detail(db: Session, *, user_id: int, transcription_id: str) -> TranscriptionDetail:
    transcription = (
        db.query(TranscriptionModel)
        .filter(TranscriptionModel.id == transcription_id, TranscriptionModel.user_id == user_id)
        .first()
    )
    if not transcription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcription not found")

    return TranscriptionDetail(
        id=transcription.id,
        title=transcription.title,
        course_name=transcription.course_name,
        audio_url=transcription.audio_url,
        transcript_text=transcription.transcript_text,
        summary_text=transcription.summary_text,
        duration_seconds=transcription.duration_seconds,
        duration=_format_duration(transcription.duration_seconds),
        word_count=transcription.word_count,
        status=transcription.status,
        created_at=transcription.created_at,
        updated_at=transcription.updated_at,
        error_message=transcription.error_message,
    )


def process_transcription_job(db: Session, transcription_id: str) -> None:
    transcription = db.query(TranscriptionModel).filter(TranscriptionModel.id == transcription_id).first()
    if not transcription:
        return

    transcription.status = TranscriptionStatus.PROCESSING
    transcription.error_message = None
    db.commit()

    try:
        audio_path = Path(transcription.audio_path)
        if not audio_path.exists():
            raise RuntimeError(f"Stored audio file not found at {audio_path}")

        transcription.duration_seconds = _extract_duration_seconds(audio_path)

        # If OpenAI key isn't configured, create a safe stubbed transcript so
        # the system can be run locally without failing.
        if not openai.api_key:
            # Create a lightweight stub so the front-end doesn't block
            transcript_text = (
                "[TRANSCRIPT STUB] OpenAI API key not configured. "
                "Install and set OPENAI_API_KEY to enable real transcriptions."
            )
        else:
            with audio_path.open("rb") as audio_file:
                transcription_result = openai.Audio.transcriptions.create(
                    model=TRANSCRIPTION_MODEL,
                    file=audio_file,
                )

            transcript_text = transcription_result.text
        transcription.transcript_text = transcript_text
        transcription.word_count = len(transcript_text.split())

        # Try to generate a summary only if we have an API key. If not,
        # leave a short note and an empty summary so the frontend can proceed.
        if openai.api_key:
            transcription.summary_text = _generate_summary(transcript_text)
        else:
            transcription.summary_text = (
                "[SUMMARY SKIPPED] OpenAI API key not configured; summary omitted."
            )
        if not transcription.course_name:
            transcription.course_name = (
                _infer_course_name(transcript_text) if openai.api_key else "General Studies"
            )

        transcription.status = TranscriptionStatus.COMPLETED
    except Exception as exc:
        transcription.status = TranscriptionStatus.FAILED
        transcription.error_message = str(exc)
        db.commit()
        raise
    else:
        db.commit()


def _apply_history_filter(query, filter_value: Optional[str]):
    if not filter_value:
        return query

    now = datetime.utcnow()
    if filter_value == "today":
        start = datetime(now.year, now.month, now.day)
    elif filter_value == "week":
        start = now - timedelta(days=7)
    elif filter_value == "month":
        start = now - timedelta(days=30)
    else:
        return query

    return query.filter(TranscriptionModel.created_at >= start)


def _format_duration(seconds: Optional[int]) -> Optional[str]:
    if seconds is None:
        return None
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(secs):02d}"


def _extract_duration_seconds(path: Path) -> Optional[int]:
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return int(float(result.stdout.strip()))
    except Exception:
        return None


def _generate_summary(transcript_text: str) -> str:
    if not transcript_text:
        return ""

    prompt = (
        "You are a note-taking assistant. Create organized study notes with sections "
        "Overview, Key Points, Important Terms, and Action Items using concise Markdown."
    )
    response = openai.ChatCompletion.create(
        model=SUMMARY_MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": transcript_text},
        ],
        temperature=0.3,
    )
    return response.choices[0].message["content"].strip()


def _infer_course_name(transcript_text: str) -> Optional[str]:
    if not transcript_text:
        return None

    response = openai.ChatCompletion.create(
        model=SUMMARY_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Read the lecture transcript and reply with a short course or subject label "
                    "(max 5 words). If unsure, respond with 'General Studies'."
                ),
            },
            {"role": "user", "content": transcript_text},
        ],
        temperature=0.2,
        max_tokens=30,
    )
    return response.choices[0].message["content"].strip()