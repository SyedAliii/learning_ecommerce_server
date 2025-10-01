from fastapi import Request, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from ..logging import log_exception
from .product_handlers import ProductNotAddedException, AllProductsNotGetException, product_not_added_exception_handler, all_products_not_get_exception_handler
from .user_handlers import UserNotCreatedException, user_not_created_exception_handler

def setup_exception_handlers(app: FastAPI):
    app.exception_handler(ProductNotAddedException)(product_not_added_exception_handler)
    app.exception_handler(AllProductsNotGetException)(all_products_not_get_exception_handler)

    app.exception_handler(UserNotCreatedException)(user_not_created_exception_handler)
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        log_exception(exc)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error occurred."}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        log_exception(exc)
        return JSONResponse(
            status_code=422,
            content={"error": exc.errors()}
        )
