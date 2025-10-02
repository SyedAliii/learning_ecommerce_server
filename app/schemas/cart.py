from typing import List
from pydantic import BaseModel
from typing import Optional

class CartAddRequest(BaseModel):
    product_id: int
    quantity: Optional[int] = 1

class CartRemoveRequest(BaseModel):
    product_id: int

# class ProductUpdateRequest(BaseModel):
#     id: int
#     title: Optional[str] = None
#     description: Optional[str] = None
#     price: Optional[int] = None
#     discount: Optional[int] = None
#     quantity: Optional[int] = None
#     category: Optional[str] = None
#     subcategory: Optional[str] = None