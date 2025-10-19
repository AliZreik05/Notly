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

    pw = payload.password
    print(
        "[signup] pw repr:", repr(pw),
        "| chars:", len(pw),
        "| bytes:", len(pw.encode("utf-8"))
    )

    MAX_BCRYPT_BYTES = 72
    if len(payload.password.encode("utf-8")) > MAX_BCRYPT_BYTES:
        raise HTTPException(
            status_code=422,
            detail=f"Password is {len(payload.password.encode('utf-8'))} bytes (>72)"
        )


    try:
        hashed_password = pwd_context.hash(payload.password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"hashing error: {e}"
        )


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