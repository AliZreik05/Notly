from datetime import datetime, timedelta, timezone
from typing import Optional
from typing import Optional
import os

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import jwt

from db.models import User
from Schemas.SignIn import UserLogin, SignInResponse
from dotenv import load_dotenv

load_dotenv()

# --- Env & defaults (avoid crashes if vars are missing) ---
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "15"))
except ValueError:
    ACCESS_TOKEN_EXPIRE_MINUTES = 15

if not SECRET_KEY:
    # Fail clearly at startup if secret is missing
    raise RuntimeError("JWT_SECRET_KEY is not set in environment/.env")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token. Compatible with Python 3.9 (no `| None`).
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # PyJWT accepts a datetime for "exp"
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # PyJWT>=2 returns str on Py3
    return token


def signin_user(payload: UserLogin, db: Session) -> SignInResponse:
    email = payload.email.lower().strip()

    user = db.query(User).filter(User.email == email).first()
    if not user or not pwd_context.verify(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    minutes = (60 * 24 * 7) if getattr(payload, "rememberMe", False) else ACCESS_TOKEN_EXPIRE_MINUTES
    token = _create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=timedelta(minutes=minutes),
    )

    return SignInResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        message="Login successful",
    )