
import shutil
from typing import List
from app.models.categories_subcategories import CategorySubcategory
from app.models.product_image import ProductImage
from app.models.category import Category
from app.models.subcategory import Subcategory
from app.schemas.product import (AllProductsGetResponse, ProductAddRequest, ProductBaseModel, SingleProductGetRequest, SingleProductGetResponse,
    ProductUpdateRequest, GetAllCategoriesSubcategoriesResponse, GetAllSubcategoriesResponse)
from app.schemas.generic import GenericResponse
from app.models.product import Product, ProductStatus
from app.models.user import UserRole, User
from fastapi import status, UploadFile
from sqlalchemy.orm import Session
from app.core.exceptions.exception_main import GenericException
from app.core.config import settings
import os
import app.utils.str_helper as str_helper
from app.integrations.cloudinary_service import upload_image
from app.utils.str_helper import generate_unique_uuid

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def __upload_image_to_cloudinary(self, image: UploadFile, image_id: str):
        try:
            success, result = upload_image(image, image_id)
            if success:
                return True, result
            else:
                return False, f"Error uploading image against id: {image_id} : {result}"
        except Exception as e:
            return False, f"Error uploading image against id: {image_id} : {str(e)}"

    def add(self, product_add_request: ProductAddRequest, user_id: int):
        try:
            if user_id is None:
                raise GenericException(reason="User not authenticated")
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if user.roles != UserRole.ADMIN:
                raise GenericException(reason="User not authorized to add products")

            if not self.db.query(Category).filter(Category.id == product_add_request.category_id).first():
                raise GenericException(reason=f"Category not found with id: {product_add_request.category_id}")
            if not self.db.query(Subcategory).filter(Subcategory.id == product_add_request.subcategory_id).first():
                raise GenericException(reason=f"Subcategory not found with id: {product_add_request.subcategory_id}")

            new_product = Product()
            new_product.id = str_helper.generate_unique_uuid()
            new_product.title = product_add_request.title
            new_product.description = product_add_request.description
            new_product.price = product_add_request.price
            new_product.quantity = product_add_request.quantity
            new_product.category_id = product_add_request.category_id
            new_product.subcategory_id = product_add_request.subcategory_id
            new_product.status = ProductStatus.AVAILABLE
            new_product.url_slug = str_helper.generate_product_slug(new_product.category_id, new_product.subcategory_id,
                new_product.title, new_product.id)

            upload_errors : List[str] = []

            for image in product_add_request.images:
                new_product_image = ProductImage()
                unique_id = str_helper.generate_unique_uuid()
                upload_status, url = self.__upload_image_to_cloudinary(image, unique_id)
                if not upload_status:
                    upload_errors.append(f"Error uploading product: {new_product.id} with image id: {unique_id}: {url}")
                new_product_image.url = url
                new_product_image.product_id = new_product.id
                self.db.add(new_product_image)
            
            self.db.add(new_product)
            self.db.commit()
            self.db.refresh(new_product)
            
            upload_errors_str = "; ".join(upload_errors)

            return GenericResponse(
                status_code=status.HTTP_201_CREATED,
                msg = f"Product successfully added. Failed Images Errors: {upload_errors_str} " if len(upload_errors) > 0 else "Product successfully added.",
            )
        except GenericException:
            raise
        except Exception as e:
            self.db.rollback()
            # self.backtrace
            raise GenericException(reason=str(e))

    def get_all(self):
        try:
            products = self.db.query(Product).filter(Product.status == ProductStatus.AVAILABLE).all()
            product_list = []
            for product in products:
                product_data = product.__dict__
                product_images : List[ProductImage] = product.images
                product_model = ProductBaseModel(**product_data, product_img_urls=[img.url for img in product_images])
                product_list.append(product_model)

            return AllProductsGetResponse(products=product_list)
        except GenericException:
            raise
        except Exception as e:
            raise GenericException(reason=str(e))
        
    def get_single(self, get_req: SingleProductGetRequest):
        try:
            url_slug = f"{get_req.category_id}/{get_req.subcategory_id}/{get_req.title}/{get_req.id}"
            product = self.db.query(Product).filter(Product.url_slug == url_slug and Product.status == ProductStatus.AVAILABLE).first()
            if not product:
                raise GenericException(reason=f"Product not found with id: {get_req.id}")
            
            product_images : List[ProductImage] = product.images
            return SingleProductGetResponse(product=ProductBaseModel(**product.__dict__,
                        product_img_urls=[img.url for img in product_images]))
        except GenericException:
            raise
        except Exception as e:
            raise GenericException(reason=f"Error getting product with id {get_req.id}: {str(e)}")

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
        
    def get_all_categories_subcategories(self):
        try:
            categories = self.db.query(Category).all()
            
            cat_subcat_list: dict[str, List[str]] = {}
            for cat in categories:
                sub = self.db.query(CategorySubcategory).filter(CategorySubcategory.category_id == cat.id).all()
                ls = [s.subcategory_id for s in sub]
                cat_subcat_list[cat.id] = ls
            return GetAllCategoriesSubcategoriesResponse(categories_subcategories=cat_subcat_list)
        except GenericException:
            raise
        except Exception as e:
            raise GenericException(reason=str(e))