from fastapi import APIRouter, status
from Schemas.Flashcards import FlashcardRequest, FlashcardResponse
from Controllers.FlashCardGenerator import generate_flashcards

router = APIRouter(prefix="/flashcards", tags=["Flashcards"])

@router.get("/", status_code=status.HTTP_200_OK)
def ping_flashcards():
    return {"message": "Flashcards endpoint is live"}

@router.post("/", response_model=FlashcardResponse, status_code=status.HTTP_200_OK)
def create_flashcards(payload: FlashcardRequest):
    """
    Send either:
      - source_text: raw text, OR
      - bullets: list of strings
    Optionally set max_cards (default 20).
    """
    return generate_flashcards(payload)