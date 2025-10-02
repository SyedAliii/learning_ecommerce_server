from fastapi import Request, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from ..logging import log_exception

class GenericException(Exception):
    def __init__(self, reason: str):
        self.reason = reason

class InvalidCredentialsException(Exception):
    def __init__(self, reason: str):
        self.reason = reason

def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(GenericException)
    async def generic_exception_handler(request: Request, exc: GenericException):
        log_exception(exc)
        return JSONResponse(
            status_code=400,
            content={"Generic Exception": f"{exc.reason}"}
        )

    @app.exception_handler(InvalidCredentialsException)
    async def invalid_credentials_exception_handler(request: Request, exc: InvalidCredentialsException):
        log_exception(exc)
        return JSONResponse(
            status_code=401,
            content={"error": f"Invalid credentials for user: {exc.reason}"}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        log_exception(exc)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error occurred. Error: " + str(exc)}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        log_exception(exc)
        return JSONResponse(
            status_code=422,
            content={"error": exc.errors()}
        )
