from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.sessions import get_db
from Schemas.SignIn import UserLogin, SignInResponse
from Controllers.SignIn import signin_user

router = APIRouter(prefix="/signin", tags=["SignIn"])

@router.post("/", response_model=SignInResponse, status_code=status.HTTP_200_OK)
def signin(payload: UserLogin, db: Session = Depends(get_db)):
    return signin_user(payload, db)

@router.get("/")
def ping_signin():
    return {"message": "SignIn endpoint is live"}