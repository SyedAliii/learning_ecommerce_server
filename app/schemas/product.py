from typing import List
from pydantic import BaseModel, ConfigDict
from typing import Optional
from fastapi import File, Form, UploadFile

class ProductAddRequest(BaseModel):
    # model_config = ConfigDict(extra='forbid')
    title: str
    description: str
    price: int
    quantity: int
    category_id: str
    subcategory_id: str
    images: List[UploadFile] = []
    
    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        description: str = Form(...),
        price: float = Form(...),
        quantity: int = Form(...),
        category_id: str = Form(...),
        subcategory_id: str = Form(...),
        images: List[UploadFile] = File(...)
    ):
        return cls(title=title, description=description, price=price,
            quantity=quantity, category_id=category_id, subcategory_id=subcategory_id, images=images)

class ProductBaseModel(BaseModel):
    id: str
    title: str
    description: str
    price: int
    quantity: int
    category_id: str
    subcategory_id: str
    url_slug: str
    product_img_urls: List[str] = []

class AllProductsGetResponse(BaseModel):
    products: List[ProductBaseModel]

class SingleProductGetRequest(BaseModel):
    title: str
    category_id: str
    subcategory_id: str
    id: str

class SingleProductGetResponse(BaseModel):
    product: ProductBaseModel

class ProductUpdateRequest(BaseModel):
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    quantity: Optional[int] = None
    category_id: Optional[str] = None
    subcategory_id: Optional[str] = None

class GetAllCategoriesSubcategoriesResponse(BaseModel):
    categories_subcategories: dict[str, List[str]]

class GetAllSubcategoriesResponse(BaseModel):
    subcategories: List[str]

class AddNewCategoryRequest(BaseModel):
    category: str
    subcategories: List[str]

class RenameCategoryRequest(BaseModel):
    category: str
    new_name: str

class RenameSubcategoryRequest(BaseModel):
    subcategory: str
    new_name: str

class EditCategoryRequest(BaseModel):
    category: str
    subcategories: List[str]
    
class DeleteCategoryRequest(BaseModel):
    category: str