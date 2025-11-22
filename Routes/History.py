from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db.sessions import get_db
from db.models import Exam
from Schemas.History import ExamHistoryItem

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/", response_model=List[ExamHistoryItem])
def get_history(user_id: int, db: Session = Depends(get_db)):
    exams = (
        db.query(Exam)
        .filter(Exam.user_id == user_id)
        .order_by(Exam.created_at.desc())
        .all()
    )
    return exams
