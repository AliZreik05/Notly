from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from db.models import User
from Schemas.SignUp import SignUpRequest, SignUpResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(payload: SignUpRequest, db: Session) -> SignUpResponse:
    email = payload.email.lower().strip()

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered."
        )

    if len(payload.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long."
        )

    hashed_password = pwd_context.hash(payload.password)

    user = User(
        firstName=payload.firstName,
        lastName=payload.lastName,
        email=email,
        password_hash=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return SignUpResponse(
        id=user.id,
        email=user.email,
        message="User created successfully"
    )