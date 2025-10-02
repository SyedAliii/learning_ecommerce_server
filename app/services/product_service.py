
from ..schemas.product import (AllProductsGetResponse, ProductAddRequest, ProductBaseModel, SingleProductGetResponse,
    ProductUpdateRequest)
from ..schemas.generic import GenericResponse
from ..models.product import Product
from ..models.user import UserRole, User
from fastapi import status
from sqlalchemy.orm import Session
from ..core.exceptions.exception_main import GenericException

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def add(self, product_add_request: ProductAddRequest, user_id: int):
        try:
            if user_id is None:
                raise GenericException(reason="User not authenticated")
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if user.roles != UserRole.ADMIN:
                raise GenericException(reason="User not authorized to add products")

            new_product = Product()
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
            
            return GenericResponse(
                status_code=status.HTTP_201_CREATED,
                msg=f"Product successfully added"
            )
        except GenericException:
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))

    def get_all(self):
        try:
            products = self.db.query(Product).all()
            return AllProductsGetResponse(products=[ProductBaseModel(**product.__dict__) for product in products])
        except GenericException:
            raise
        except Exception as e:
            raise GenericException(reason=str(e))
        
    def get_single(self, product_id: int):
        try:
            product = self.db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise GenericException(reason=f"Product not found with id: {product_id}")
            return SingleProductGetResponse(product=ProductBaseModel(**product.__dict__))
        except GenericException:
            raise
        except Exception as e:
            raise GenericException(reason=f"Error getting product with id {product_id}: {str(e)}")

    def update(self, product_update_request: ProductUpdateRequest, user_id: int):
        try:
            if user_id is None:
                raise GenericException(reason="User not authenticated")

            user = self.db.query(User).filter(User.id == user_id).first()
            if user.roles != UserRole.ADMIN:
                raise GenericException(reason="User not authorized to update products")

            product = self.db.query(Product).filter(Product.id == product_update_request.id).first()
            if not product:
                raise GenericException(reason="Product not found")

            update_data = product_update_request.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(product, field, value)

            self.db.commit()
            self.db.refresh(product)

            return GenericResponse(
                status_code=status.HTTP_200_OK,
                msg=f"Product successfully updated"
            )
        except GenericException:
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))

    def delete(self, product_id: int, user_id: int):
        try:
            if user_id is None:
                raise GenericException(reason="User not authenticated")

            user = self.db.query(User).filter(User.id == user_id).first()
            if user.roles != UserRole.ADMIN:
                raise GenericException(reason="User not authorized to delete products")

            product = self.db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise GenericException(reason="Product not found")

            self.db.delete(product)
            self.db.commit()

            return GenericResponse(
                status_code=status.HTTP_200_OK,
                msg=f"Product successfully deleted"
            )
        except GenericException:
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))