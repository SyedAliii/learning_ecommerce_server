from typing import List
from pydantic import BaseModel
from typing import Optional
from fastapi import File, Form, UploadFile

class ProductAddRequest(BaseModel):
    title: str
    description: str
    price: int
    quantity: int
    category: str
    subcategory: str
    images: List[UploadFile] = []
    
    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        description: str = Form(...),
        price: float = Form(...),
        quantity: int = Form(...),
        category: str = Form(...),
        subcategory: str = Form(...),
        images: List[UploadFile] = File(...)
    ):
        return cls(title=title, description=description, price=price,
            quantity=quantity, category=category, subcategory=subcategory, images=images)

class ProductBaseModel(BaseModel):
    id: str
    title: str
    description: str
    price: int
    quantity: int
    category: str
    subcategory: str
    images: List[str] = []

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