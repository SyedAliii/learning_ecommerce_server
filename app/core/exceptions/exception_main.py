from fastapi import Request, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from ..logging import log_exception
from .product_handlers import ProductNotAddedException, AllProductsNotGetException, product_not_added_exception_handler, all_products_not_get_exception_handler
from .user_handlers import UserNotCreatedException, user_not_created_exception_handler

class InvalidCredentialsException(Exception):
    def __init__(self, reason: str):
        self.reason = reason

def setup_exception_handlers(app: FastAPI):
    app.exception_handler(ProductNotAddedException)(product_not_added_exception_handler)
    app.exception_handler(AllProductsNotGetException)(all_products_not_get_exception_handler)

    app.exception_handler(UserNotCreatedException)(user_not_created_exception_handler)
    
    app.exception_handler(InvalidCredentialsException)
    async def invalid_credentials_exception_handler(exc: InvalidCredentialsException):
        log_exception(exc)
        return JSONResponse(
            status_code=401,
            content={"error": f"Invalid credentials for user {exc.user_id}: {exc.reason}"}
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
