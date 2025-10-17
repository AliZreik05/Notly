from fastapi import APIRouter, status
from Schemas.SignOut import UserLogOut
from Controllers.SignOut import logout_user

router = APIRouter(prefix="/SignOut", tags=["SignOut"])

@router.post("/", response_model=UserLogOut, status_code=status.HTTP_200_OK)
def signout():
    return logout_user()

@router.get("/")
def ping_signout():
    return {"message": "SignOut endpoint is live"}