from typing import List
from pydantic import BaseModel

class ProductAddRequest(BaseModel):
    title: str
    description: str
    price: int
    discount: int
    quantity: int
    category: str
    subcategory: str

class ProductAddResponse(BaseModel):
    status_code: int
    msg: str

class ProductResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    discount: int
    quantity: int
    category: str
    subcategory: str

class AllProductsGetResponse(BaseModel):
    products: List[ProductResponse]