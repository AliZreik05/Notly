from pydantic import BaseModel

class LectureOut(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True   # orm_mode=True if you use old pydantic
