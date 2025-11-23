from pydantic import BaseModel
from typing import List,Optional
from datetime import datetime

class ExamHistoryItem(BaseModel):
    id: int
    title: str
    grade: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
