from fastapi import Request
from fastapi.responses import JSONResponse

class ProductNotAddedException(Exception):
    def __init__(self, reason: str):
        self.reason = reason

class AllProductsNotGetException(Exception):
    def __init__(self, reason: str):
        self.reason = reason

async def product_not_added_exception_handler(request: Request, exc: ProductNotAddedException):
    return JSONResponse(
        status_code=400,
        content={
            "error": f"Product {exc.product_id} could not be added. Reason: {exc.reason}"
        },
    )

async def all_products_not_get_exception_handler(request: Request, exc: AllProductsNotGetException):
    return JSONResponse(
        status_code=404,
        content={
            "error": f"All products could not be retrieved. Reason: {exc.reason}"
        },
    )