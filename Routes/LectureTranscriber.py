from typing import List, Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, status, Query
from sqlalchemy.orm import Session

from db.sessions import get_db
from Controllers.transcription_controller import (
    create_transcription_request,
    list_transcriptions_for_history,
    get_transcription_detail,
)
from Schemas.transcription_schema import (
    TranscriptionUploadResponse,
    TranscriptionHistoryItem,
    TranscriptionDetail,
)

router = APIRouter(prefix="/api/v1/transcriptions", tags=["Transcriptions"])


@router.post(
    "/upload",
    response_model=TranscriptionUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_transcription(
    user_id: int = Query(..., description="Authenticated user identifier"),
    title: str = Form(...),
    course_name: Optional[str] = Form(default=None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    transcription = await create_transcription_request(
        db,
        user_id=user_id,
        file=file,
        title=title,
        course_name=course_name,
    )
    return TranscriptionUploadResponse(id=transcription.id, status=transcription.status)


@router.get("/history", response_model=List[TranscriptionHistoryItem])
def get_transcription_history(
    user_id: int = Query(..., description="Authenticated user identifier"),
    filter: Optional[str] = Query(
        default=None, pattern="^(today|week|month)$", description="Date filter"
    ),
    db: Session = Depends(get_db),
):
    return list_transcriptions_for_history(db, user_id=user_id, filter_value=filter)


@router.get("/{transcription_id}", response_model=TranscriptionDetail)
def get_transcription(
    transcription_id: str,
    user_id: int = Query(..., description="Authenticated user identifier"),
    db: Session = Depends(get_db),
):
    return get_transcription_detail(db, user_id=user_id, transcription_id=transcription_id)


@router.get("/{transcription_id}/status", response_model=TranscriptionUploadResponse)
def get_transcription_status(
    transcription_id: str,
    user_id: int = Query(..., description="Authenticated user identifier"),
    db: Session = Depends(get_db),
):
    detail = get_transcription_detail(db, user_id=user_id, transcription_id=transcription_id)
    return TranscriptionUploadResponse(id=detail.id, status=detail.status)