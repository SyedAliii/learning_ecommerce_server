from pydantic import BaseModel, EmailStr
from ..models.users import UserRole
from typing import Optional
from datetime import timedelta

class UserCreateRequest(BaseModel):
    id: int
    name: str
    email: EmailStr
    password: str
    address: str
    city: str
    country: str
    roles: UserRole

class UserCreateResponse(BaseModel):
    status_code: int
    msg: str

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