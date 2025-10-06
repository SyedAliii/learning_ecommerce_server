from fastapi import FastAPI
from app.db.session import engine, Base
from app.core.exceptions.exception_main import setup_exception_handlers
from app.api.v1.routes import (products as products_v1, users as users_v1,
    cart as cart_v1, order as order_v1)
from fastapi.staticfiles import StaticFiles

app = FastAPI()

Base.metadata.create_all(bind=engine)

setup_exception_handlers(app)

app.mount("/assets", StaticFiles(directory="app/assets"), name="assets")

app.include_router(products_v1.router, prefix="/v1", tags=["products-v1"])
app.include_router(users_v1.router, prefix="/v1", tags=["users-v1"])
app.include_router(cart_v1.router, prefix="/v1", tags=["cart-v1"])
app.include_router(order_v1.router, prefix="/v1", tags=["order-v1"])