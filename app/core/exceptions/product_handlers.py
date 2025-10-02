from fastapi import Request
from fastapi.responses import JSONResponse

# class ProductNotAddedException(Exception):
#     def __init__(self, reason: str):
#         self.reason = reason

# async def product_not_added_exception_handler(request: Request, exc: ProductNotAddedException):
#     return JSONResponse(
#         status_code=400,
#         content={
#             "error": f"Product could not be added. Reason: {exc.reason}"
#         },
#     )