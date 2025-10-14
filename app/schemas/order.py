from typing import List
from pydantic import BaseModel
from typing import Optional
from app.models.order import OrderStatus

class OrderShippedRequest(BaseModel):
    user_id: int
    cart_id: int

class OrderDeliveredRequest(BaseModel):
    user_id: int
    cart_id: int

class ProductPriceBreakdown(BaseModel):
    title: str
    price: int
    quantity: int

class OrderConfirmResponse(BaseModel):
    id: int
    subtotal: int
    tax: int
    shipping_fee: int
    grand_total: int
    products: List[ProductPriceBreakdown]
    order: OrderStatus
    status_code: int
    msg: str

class OrderShippedResponse(BaseModel):
    id: int
    subtotal: int
    tax: int
    shipping_fee: int
    grand_total: int
    products: List[ProductPriceBreakdown]
    order: OrderStatus
    status_code: int
    msg: str

class OrderDeliveredResponse(BaseModel):
    id: int
    subtotal: int
    tax: int
    shipping_fee: int
    grand_total: int
    products: List[ProductPriceBreakdown]
    order: OrderStatus
    status_code: int
    msg: str

class OrderBaseModel(BaseModel):
    id: int
    user_id: int
    username: str
    user_email: str
    cart_id: int
    total_items: int
    total_price: int
    status: OrderStatus

class GetAllOrdersResponse(BaseModel):
    orders: List[OrderBaseModel]
    status_code: int
    msg: str