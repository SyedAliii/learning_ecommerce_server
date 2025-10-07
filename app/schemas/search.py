from typing import List
from pydantic import BaseModel, ConfigDict
from typing import Optional
from fastapi import File, Form, UploadFile
from app.schemas.product import ProductBaseModel

class SearchResponse(BaseModel):
    status_code: int
    msg: str
    products: Optional[List[ProductBaseModel]] = []
    