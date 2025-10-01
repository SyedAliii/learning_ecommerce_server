from fastapi import Request
from fastapi.responses import JSONResponse

class UserNotCreatedException(Exception):
    def __init__(self, user_id: int, reason: str):
        self.user_id = user_id
        self.reason = reason

class AuthFailedException(Exception):
    def __init__(self, email: str, reason: str):
        self.email = email
        self.reason = reason

async def user_not_created_exception_handler(request: Request, exc: UserNotCreatedException):
    return JSONResponse(
        status_code=400,
        content={
            "error": f"User {exc.user_id} could not be created. Reason: {exc.reason}"
        },
    )

async def auth_failed_exception_handler(request: Request, exc: AuthFailedException):
    return JSONResponse(
        status_code=400,
        content={
            "error": f"Authentication failed for user {exc.user_id}. Reason: {exc.reason}"
        },
    )