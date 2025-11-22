from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db.sessions import get_db
from db.models import Note
from Schemas.Lecture import LectureOut

router = APIRouter(prefix="/lectures", tags=["lectures"])

@router.post("/create")
def create_lecture(title: str, user_id: int, db: Session = Depends(get_db)):
    lecture = Note(title=title, content="test content", user_id=user_id)
    db.add(lecture)
    db.commit()
    db.refresh(lecture)
    return lecture


@router.get("/", response_model=List[LectureOut])
def list_lectures(user_id: int, db: Session = Depends(get_db)):
    notes = (
        db.query(Note)
        .filter(Note.user_id == user_id)
        .order_by(Note.created_at.desc())
        .all()
    )
    return notes
