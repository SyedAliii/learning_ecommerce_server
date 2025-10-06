
import shutil
from app.models.product_image import ProductImage
from ..schemas.product import (AllProductsGetResponse, ProductAddRequest, ProductBaseModel, SingleProductGetResponse,
    ProductUpdateRequest)
from ..schemas.generic import GenericResponse
from ..models.product import Product, ProductStatus
from ..models.user import UserRole, User
from fastapi import status, UploadFile
from sqlalchemy.orm import Session
from ..core.exceptions.exception_main import GenericException
from app.core.config import settings
import os
import app.utils.str_helper as str_helper

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def __save_image(self, image: UploadFile, product_id: str):
        file_path = os.path.join(settings.PRODUCT_IMAGES_DIR, str(image.filename))
        with open(os.path.join(settings.ROOT_FOLDER, file_path), "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        return os.path.join(settings.URL, file_path)

    def add(self, product_add_request: ProductAddRequest, user_id: int):
        try:
            if user_id is None:
                raise GenericException(reason="User not authenticated")
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if user.roles != UserRole.ADMIN:
                raise GenericException(reason="User not authorized to add products")

            new_product = Product()
            new_product.id = str_helper.generate_unique_uuid()
            new_product.title = product_add_request.title
            new_product.description = product_add_request.description
            new_product.price = product_add_request.price
            new_product.quantity = product_add_request.quantity
            new_product.category = product_add_request.category
            new_product.subcategory = product_add_request.subcategory
            new_product.status = ProductStatus.AVAILABLE

            for image in product_add_request.images:
                new_product_image = ProductImage()
                new_product_image.url = self.__save_image(image, new_product.id)
                new_product_image.product_id = new_product.id
                self.db.add(new_product_image)
            
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
            products = self.db.query(Product).filter(Product.status == ProductStatus.AVAILABLE).all()
            return AllProductsGetResponse(products=[ProductBaseModel(**product.__dict__) for product in products])
        except GenericException:
            raise
        except Exception as e:
            raise GenericException(reason=str(e))
        
    def get_single(self, product_id: str):
        try:
            product = self.db.query(Product).filter(Product.id == product_id and Product.status == ProductStatus.AVAILABLE).first()
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

    def delete(self, product_id: str, user_id: int):
        try:
            if user_id is None:
                raise GenericException(reason="User not authenticated")

            user = self.db.query(User).filter(User.id == user_id).first()
            if user.roles != UserRole.ADMIN:
                raise GenericException(reason="User not authorized to delete products")

            product = self.db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise GenericException(reason="Product not found")

            product.status = ProductStatus.DELISTED
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