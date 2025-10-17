from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.sessions import get_db
from Schemas.SignUp import SignUpRequest, SignUpResponse
from Controllers.SignUp import create_user

router = APIRouter(prefix="/signup", tags=["SignUp"])

@router.post("/", response_model=SignUpResponse, status_code=status.HTTP_201_CREATED)
def signup_user(payload: SignUpRequest, db: Session = Depends(get_db)):
    return create_user(payload, db)

@router.get("/")
def get_signup_page():
    return {"message": "SignUp endpoint is live"}
