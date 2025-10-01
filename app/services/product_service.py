
from ..schemas.product import AllProductsGetResponse, ProductAddRequest, ProductAddResponse, ProductResponse
from ..models.product import Product
from fastapi import Depends, status
from sqlalchemy.orm import Session
from ..core.exceptions.product_handlers import ProductNotAddedException, AllProductsNotGetException

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def add(self, product_add_request: ProductAddRequest):
        try:
            new_product = Product()
            new_product.id = product_add_request.id
            new_product.title = product_add_request.title
            new_product.description = product_add_request.description
            new_product.price = product_add_request.price
            new_product.discount = product_add_request.discount
            new_product.quantity = product_add_request.quantity
            new_product.category = product_add_request.category
            new_product.subcategory = product_add_request.subcategory

            self.db.add(new_product)
            self.db.commit()
            self.db.refresh(new_product)
            
            return ProductAddResponse(
                status_code=status.HTTP_201_CREATED,
                msg=f"Product Id: {new_product.id} successfully added"
            )
        except Exception as e:
            self.db.rollback()
            raise ProductNotAddedException(product_id=product_add_request.id, reason=str(e))

    def get_all(self):
        try:
            products = self.db.query(Product).all()
            return AllProductsGetResponse(products=[ProductResponse(**product.__dict__) for product in products])
        except Exception as e:
            raise AllProductsNotGetException(reason=str(e))