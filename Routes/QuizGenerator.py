from fastapi import APIRouter, status
from Schemas.QuizGenerator import QuizRequest, QuizResponse
from Controllers.QuizGenerator import generate_quiz

router = APIRouter(prefix="/QuizGenerator", tags=["QuizGenerator"])

@router.post("/", response_model=QuizResponse, status_code=status.HTTP_200_OK)
def create_quiz(payload: QuizRequest):
    """
    Provide either: 
      - topic (string) 
      - source_text (string)
    Optionally both. Returns MCQs.
    """
    return generate_quiz(payload)

@router.get("/")
def ping_quiz():
    return {"message": "QuizGenerator endpoint is live"}
