# routers/password.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from db.sessions import get_db
from db.models import User  # adjust to your user model
from Controllers.utils import get_password_hash  # whatever you use already

router = APIRouter(prefix="/password", tags=["Password"])

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str

@router.post("/reset")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = get_password_hash(payload.new_password)
    db.add(user)
    db.commit()

    return {"message": "Password updated successfully"}
