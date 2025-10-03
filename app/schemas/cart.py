from typing import List
from pydantic import BaseModel
from typing import Optional

class CartAddRequest(BaseModel):
    product_id: int
    quantity: Optional[int] = 1

class CartRemoveRequest(BaseModel):
    product_id: int
    quantity: Optional[int] = 1