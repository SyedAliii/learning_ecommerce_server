from fastapi import Request
from fastapi.responses import JSONResponse

class AuthFailedException(Exception):
    def __init__(self, email: str, reason: str):
        self.email = email
        self.reason = reason

async def auth_failed_exception_handler(request: Request, exc: AuthFailedException):
    return JSONResponse(
        status_code=400,
        content={
            "error": f"Authentication failed for user {exc.user_id}. Reason: {exc.reason}"
        },
    )