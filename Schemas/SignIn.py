from pydantic import BaseModel, EmailStr, ConfigDict

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    rememberMe: bool = False
    model_config = ConfigDict(from_attributes=True)

class SignInResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    message: str = "Login successful"
    model_config = ConfigDict(from_attributes=True)
