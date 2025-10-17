from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator

Difficulty = Literal["easy", "medium", "hard"]

class QuizItem(BaseModel):
    question: str = Field(..., min_length=3)
    options: List[str] = Field(..., min_length=2)
    answer_index: int = Field(..., ge=0)
    explanation: Optional[str] = None

    @model_validator(mode="after")
    def _validate_answer_index(self):
        if self.answer_index >= len(self.options):
            raise ValueError("answer_index must point to one of the options")
        return self

class QuizRequest(BaseModel):
    topic: Optional[str] = None
    source_text: Optional[str] = None
    num_questions: int = Field(5, ge=1, le=50)
    difficulty: Difficulty = "medium"

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def _at_least_one_source(self):
        if not self.topic and not self.source_text:
            raise ValueError("Provide at least one of: topic or source_text")
        return self

class QuizResponse(BaseModel):
    quiz_id: Optional[int] = None  # if you later persist to DB
    items: List[QuizItem]
    message: str = "Quiz generated successfully"

    model_config = ConfigDict(from_attributes=True)
