from typing import List
from pydantic import BaseModel, field_validator
from typing import Optional
from app.schemas.user import UserCartProduct

class CartAddRequest(BaseModel):
    product_id: str
    quantity: Optional[int] = 1

    @field_validator("quantity")
    def validate_quantity(cls, value):
        if value is not None and value <= 0:
            raise ValueError("quantity must be greater than 0")
        return value

class CartRemoveRequest(BaseModel):
    product_id: str
    quantity: Optional[int] = 1

    @field_validator("quantity")
    def validate_quantity(cls, value):
        if value is not None and value <= 0:
            raise ValueError("quantity must be greater than 0")
        return value

class CartViewResponse(BaseModel):
    products: List[UserCartProduct]
    status_code: int
    msg: str