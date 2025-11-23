# Routers/history.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db.sessions import get_db
from db.models import Exam, ExamSource
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


@router.post("/create-test", response_model=ExamHistoryItem)
def create_test_exam(user_id: int, db: Session = Depends(get_db)):
    exam = Exam(
        user_id=user_id,
        title="Test Quiz from backend",
        grade=8,  # out of 10, for example
        source_type=ExamSource.manual,
        source_id=None,
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam
