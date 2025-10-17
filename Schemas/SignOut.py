from pydantic import BaseModel, ConfigDict

class UserLogOut(BaseModel):
    message: str = "User logged out successfully"
    model_config = ConfigDict(from_attributes=True)
