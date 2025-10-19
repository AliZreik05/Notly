from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator

class Flashcard(BaseModel):
    front: str = Field(..., description="Question/prompt")
    back: str = Field(..., description="Answer/explanation")

class FlashcardRequest(BaseModel):
    source_text: Optional[str] = Field(default=None, description="Raw text to parse into flashcards")
    bullets: Optional[List[str]] = Field(default=None, description="Bullet points to convert")
    max_cards: int = Field(default=20, ge=1, le=100)

    @model_validator(mode="after")
    def _need_content(self):
        if not self.source_text and not self.bullets:
            raise ValueError("Provide source_text or bullets")
        return self

class FlashcardResponse(BaseModel):
    items: List[Flashcard]
    message: str = "Flashcards generated successfully"
    model_config = ConfigDict(from_attributes=True)