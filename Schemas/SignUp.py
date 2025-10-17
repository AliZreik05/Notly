from pydantic import BaseModel, EmailStr, ConfigDict, model_validator
from typing import Optional

class SignUpRequest(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    password: str
    verifyPassword: str
    rememberMe: bool = False

    @model_validator(mode="after")
    def _match_passwords(self):
        if self.password != self.verifyPassword:
            raise ValueError("Passwords do not match")
        return self

class SignUpResponse(BaseModel):
    id: int
    email: EmailStr
    message: Optional[str] = "User created successfully"
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    password: str 
    rememberMe: bool = False
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
