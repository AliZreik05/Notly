from pydantic import BaseModel
from typing import List
from datetime import datetime

class ExamHistoryItem(BaseModel):
    id: int
    title: str
    grade: int
    created_at: datetime

    class Config:
        from_attributes = True
