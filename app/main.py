from fastapi import FastAPI
from .db.session import engine, Base
from .core.exceptions.exception_main import setup_exception_handlers
from .api.v1.routes import (products as products_v1, users as users_v1, auth as auth_v1,
    cart as cart_v1, order as order_v1)

app = FastAPI()

Base.metadata.create_all(bind=engine)

setup_exception_handlers(app)

app.include_router(auth_v1.router, prefix="/v1", tags=["auth-v1"])
app.include_router(products_v1.router, prefix="/v1", tags=["products-v1"])
app.include_router(users_v1.router, prefix="/v1", tags=["users-v1"])
app.include_router(cart_v1.router, prefix="/v1", tags=["cart-v1"])
app.include_router(order_v1.router, prefix="/v1", tags=["order-v1"])