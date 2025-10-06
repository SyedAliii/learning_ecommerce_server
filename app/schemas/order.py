from typing import List
from pydantic import BaseModel
from typing import Optional
from app.models.order import OrderStatus

class OrderUpdateRequest(BaseModel):
    status: OrderStatus
    user_id: int
    cart_id: int

class ProductPriceBreakdown(BaseModel):
    title: str
    price: int
    quantity: int

class OrderUpdateResponse(BaseModel):
    id: int
    subtotal: int
    tax: int
    shipping_fee: int
    grand_total: int
    products: List[ProductPriceBreakdown]
    order: OrderStatus
    status_code: int
    msg: str
