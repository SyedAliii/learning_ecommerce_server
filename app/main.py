from fastapi import FastAPI
from app.db.session import engine, Base
from app.core.exceptions.exception_main import setup_exception_handlers
from app.api.v1.routes import (products as products_v1, users as users_v1,
    cart as cart_v1, order as order_v1, search as search_v1)
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173",  # Vite default port
    "http://localhost:8080",  # In case your dev server runs on 8080
    "http://127.0.0.1:5173",  # Some browsers resolve localhost to 127.0.0.1
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Allowed origins
    allow_credentials=True,       # Allow cookies, auth headers, etc.
    allow_methods=["*"],          # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # Allow all request headers
)

Base.metadata.create_all(bind=engine)

setup_exception_handlers(app)

app.mount("/assets", StaticFiles(directory="app/assets"), name="assets")

app.include_router(products_v1.router, prefix="/v1", tags=["products-v1"])
app.include_router(users_v1.router, prefix="/v1", tags=["users-v1"])
app.include_router(cart_v1.router, prefix="/v1", tags=["cart-v1"])
app.include_router(order_v1.router, prefix="/v1", tags=["order-v1"])
app.include_router(search_v1.router, prefix="/v1", tags=["search-v1"])