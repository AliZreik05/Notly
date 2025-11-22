from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db.sessions import get_db
from Models import Note      # wherever Note model lives
from Schemas.lecture import LectureOut

router = APIRouter(prefix="/lectures", tags=["lectures"])

@router.get("/", response_model=List[LectureOut])
def list_lectures(user_id: int, db: Session = Depends(get_db)):
    notes = (
        db.query(Note)
        .filter(Note.user_id == user_id)
        .order_by(Note.created_at.desc())
        .all()
    )
    return notes
