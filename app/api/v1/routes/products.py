import shutil
from typing import List
from app.schemas.product import (ProductAddRequest, AllProductsGetResponse, SingleProductGetRequest,
    SingleProductGetResponse, ProductUpdateRequest, GetAllCategoriesSubcategoriesResponse, GetAllSubcategoriesResponse)
from app.schemas.generic import GenericResponse
from fastapi import APIRouter, Depends, File, Form, UploadFile
from app.services.product_service import ProductService
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/add_product", response_model=GenericResponse)
async def add_product(product_add_request: ProductAddRequest = Depends(ProductAddRequest.as_form), user_id: int = Depends(get_current_user), 
                      db: Session = Depends(get_db)):
    product_service = ProductService(db)
    return product_service.add(product_add_request, user_id)

@router.get("/get_all_products", response_model=AllProductsGetResponse)
async def get_all_products(db: Session = Depends(get_db)):
    product_service = ProductService(db)
    return product_service.get_all()


@router.get("/get_single_product/{category}/{sub_category}/{title}/{id}", response_model=SingleProductGetResponse)
async def get_single_product(category: str, sub_category: str, title: str, id: str, db: Session = Depends(get_db)):
    product_service = ProductService(db)
    get_req = SingleProductGetRequest(title=title, category=category, subcategory=sub_category, id=id)
    return product_service.get_single(get_req)

@router.put("/update_product", response_model=GenericResponse)
async def update_product(product_update_request: ProductUpdateRequest, user_id: int = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    product_service = ProductService(db)
    return product_service.update(product_update_request, user_id=user_id)

@router.delete("/delete_product/{product_id}", response_model=GenericResponse)
async def delete_product(product_id: str, user_id: int = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    product_service = ProductService(db)
    return product_service.delete(product_id=product_id, user_id=user_id)

@router.get("/get_all_categories_subcategories", response_model=GetAllCategoriesSubcategoriesResponse)
async def get_all_categories_subcategories(db: Session = Depends(get_db)):
    product_service = ProductService(db)
    return product_service.get_all_categories_subcategories()

@router.post("/upload_test")
async def upload_test( title: str = Form(...), images: List[UploadFile] = File(...)):
    saved_files = []
    for image in images:
        file_path = f"assets/product_images/{image.filename}"
        with open(f"app/{file_path}", "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = f"http://localhost:8000/{file_path}"
        saved_files.append(image_url)

    return {"uploaded_files": saved_files, "title": title}