# routers/exam.py

from typing import List, Dict, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.sessions import get_db
from db.models import Exam, ExamQuestion, ExamSource

router = APIRouter(prefix="/exam", tags=["exam"])


# ---------- Schemas ----------

class ExamQuestionOut(BaseModel):
    id: int
    question: str
    options: List[str]
    order: Optional[int] = None

    class Config:
        orm_mode = True


class ExamDetail(BaseModel):
    id: int
    title: str
    created_at: datetime
    grade: Optional[int] = None
    source_type: str
    source_id: Optional[int] = None
    questions: List[ExamQuestionOut]

    class Config:
        orm_mode = True


class GradeRequest(BaseModel):
    # answers: { question_id: chosen_option_index }
    answers: Dict[int, int]


class QuestionResult(BaseModel):
    question_id: int
    correct_index: int
    user_index: Optional[int]
    is_correct: bool


class GradeResult(BaseModel):
    exam_id: int
    total_questions: int
    correct: int
    grade: int        # same as correct (you can change later)
    details: List[QuestionResult]


# ---------- Get full exam with questions ----------

@router.get("/{exam_id}", response_model=ExamDetail)
def get_exam(
    exam_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Fetch a single exam + all its questions for a given user.
    Used when user opens a quiz from history or right after creation.
    """
    exam = (
        db.query(Exam)
        .filter(Exam.id == exam_id, Exam.user_id == user_id)
        .first()
    )

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found for this user")

    # questions are loaded via relationship exam.questions
    return exam


# ---------- Grade exam ----------

@router.post("/{exam_id}/grade", response_model=GradeResult)
def grade_exam(
    exam_id: int,
    payload: GradeRequest,
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Grade an exam:
    - compares user's answers to correct indices
    - updates Exam.grade in DB (as number of correct answers)
    - returns detailed grading result
    """
    exam = (
        db.query(Exam)
        .filter(Exam.id == exam_id, Exam.user_id == user_id)
        .first()
    )

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found for this user")

    questions = (
        db.query(ExamQuestion)
        .filter(ExamQuestion.exam_id == exam.id)
        .order_by(ExamQuestion.order.asc().nullsfirst())
        .all()
    )

    if not questions:
        raise HTTPException(status_code=400, detail="Exam has no questions")

    answers = payload.answers  # {question_id: user_index}

    total = len(questions)
    correct_count = 0
    details: List[QuestionResult] = []

    for q in questions:
        user_idx = answers.get(q.id)
        is_correct = (user_idx is not None and user_idx == q.answer_idx)

        if is_correct:
            correct_count += 1

        details.append(
            QuestionResult(
                question_id=q.id,
                correct_index=q.answer_idx,
                user_index=user_idx,
                is_correct=is_correct,
            )
        )

    exam.grade = correct_count
    exam.result_details = [d.dict() for d in details]
    db.add(exam)
    db.commit()
    db.refresh(exam)

    return GradeResult(
        exam_id=exam.id,
        total_questions=total,
        correct=correct_count,
        grade=correct_count,
        details=details,
    )

@router.get("/{exam_id}/result", response_model=GradeResult)
def get_exam_result(
    exam_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):
    exam = (
        db.query(Exam)
        .filter(Exam.id == exam_id, Exam.user_id == user_id)
        .first()
    )

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found for this user")

    if not exam.result_details:
        raise HTTPException(status_code=404, detail="No stored result for this exam")

    # if result_details is JSON column:
    details_data = exam.result_details
    # if stored as Text: details_data = json.loads(exam.result_details)

    details = [QuestionResult(**item) for item in details_data]

    return GradeResult(
        exam_id=exam.id,
        total_questions=len(details),
        correct=exam.grade or 0,
        grade=exam.grade or 0,
        details=details,
    )