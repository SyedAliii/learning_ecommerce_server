from ....schemas.product import ProductAddRequest, ProductAddResponse, AllProductsGetResponse
from fastapi import APIRouter, Depends
from ....services.product_service import ProductService
from ....db.session import get_db
from sqlalchemy.orm import Session
from ...deps import get_current_user

router = APIRouter()

@router.post("/add_product", response_model=ProductAddResponse)
async def add_product(product_add_request: ProductAddRequest, user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    product_service = ProductService(db)
    return product_service.add(product_add_request, user_id)

@router.get("/get_all_products", response_model=AllProductsGetResponse)
async def get_all_products(db: Session = Depends(get_db)):
    product_service = ProductService(db)
    return product_service.get_all()