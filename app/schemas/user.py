from pydantic import BaseModel, EmailStr
from ..models.user import UserRole
from typing import Optional, List
from ..schemas.product import ProductBaseModel
from datetime import timedelta

class UserCreateRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    address: str
    city: str
    country: str

class UserAuthenticateRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    address: str
    city: str
    country: str
    roles: UserRole

class UserAuthenticateResponse(BaseModel):
    status_code: int
    msg: str
    user: UserResponse = None

class UserCartProduct(BaseModel):
    id: int
    title: str
    description: str
    price: int
    total_quantity: int
    category: str
    subcategory: str
    quantity_in_cart: int

class UserDataResponse(BaseModel):
    access_token: str
    name: str
    email: EmailStr
    roles: UserRole
    cart_products: List[UserCartProduct]
    status_code: int
    msg: str
