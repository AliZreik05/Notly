from Schemas.SignOut import UserLogOut

def logout_user() -> UserLogOut:
    """
    Logs the user out.
    For stateless JWTs, this just tells the client to delete the token.
    If you later add token blacklisting or sessions, handle that here.
    """
    return UserLogOut(message="User logged out successfully")
