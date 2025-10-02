from typing import List
from pydantic import BaseModel
from typing import Optional

class ProductAddRequest(BaseModel):
    title: str
    description: str
    price: int
    discount: int
    quantity: int
    category: str
    subcategory: str

class ProductBaseModel(BaseModel):
    id: int
    title: str
    description: str
    price: int
    discount: int
    quantity: int
    category: str
    subcategory: str

class AllProductsGetResponse(BaseModel):
    products: List[ProductBaseModel]

class SingleProductGetResponse(BaseModel):
    product: ProductBaseModel

class ProductUpdateRequest(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    discount: Optional[int] = None
    quantity: Optional[int] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None