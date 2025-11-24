from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.sessions import get_db
from db.models import User
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/reset-password", tags=["ResetPassword"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ------ SCHEMA ------
class ResetPasswordRequest(BaseModel):
    email: EmailStr
    newPassword: str
    confirmPassword: str


# ------ ENDPOINT ------
@router.post("/")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):

    # 1. Check match
    if payload.newPassword != payload.confirmPassword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    # 2. Find user
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found with this email"
        )

    # 3. Hash new password
    hashed_password = pwd_context.hash(payload.newPassword)

    # 4. Store it
    user.password_hash =  hashed_password
    db.commit()

    return {"message": "Password has been reset successfully!"}
