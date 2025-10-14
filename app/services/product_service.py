
import shutil
from typing import List
from app.models.categories_subcategories import CategorySubcategory
from app.models.product_image import ProductImage
from app.models.category import Category
from app.models.subcategory import Subcategory
from app.schemas.product import (AddNewCategoryRequest, AllProductsGetResponse, DeleteCategoryRequest, EditCategoryRequest, ProductAddRequest, ProductBaseModel, RenameCategoryRequest, RenameCategoryRequest, RenameSubcategoryRequest, SingleProductGetRequest, SingleProductGetResponse,
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

    def __check_if_any_product_belongs_to_category(self, category_id: str) -> Product:
        product = self.db.query(Product).filter(Product.category_id == category_id).first()
        return product

    def __check_if_any_product_belongs_to_subcategory(self, subcategory_id: str) -> Product:
        product = self.db.query(Product).filter(Product.subcategory_id == subcategory_id).first()
        return product

    def __check_if_subcategory_belongs_to_any_other_category(self, category_id: str, subcategory_id: str) -> bool:
        cat_subcat = self.db.query(CategorySubcategory).filter(
            (CategorySubcategory.category_id != category_id) & 
            (CategorySubcategory.subcategory_id == subcategory_id)
        ).first()
        return cat_subcat is not None

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
                url_slug = f"{str_helper.slugify(product.category_id)}/{str_helper.slugify(product.subcategory_id)}/{str_helper.slugify(product.title)}/{product.id}"
                product_model = ProductBaseModel(**product_data, url_slug=url_slug, product_img_urls=[img.url for img in product_images])
                product_list.append(product_model)

            return AllProductsGetResponse(products=product_list)
        except GenericException:
            raise
        except Exception as e:
            raise GenericException(reason=str(e))
        
    def get_single(self, req: SingleProductGetRequest):
        try:
            product = self.db.query(Product).filter(Product.id == req.id and Product.status == ProductStatus.AVAILABLE).first()
            if not product:
                raise GenericException(reason=f"Product not found with id: {req.id}")
            
            url_slug = f"{str_helper.slugify(req.category_id)}/{str_helper.slugify(req.subcategory_id)}/{str_helper.slugify(req.title)}/{req.id}"
            product_images : List[ProductImage] = product.images
            return SingleProductGetResponse(product=ProductBaseModel(**product.__dict__, url_slug=url_slug,
                        product_img_urls=[img.url for img in product_images]))
        except GenericException:
            raise
        except Exception as e:
            raise GenericException(reason=f"Error getting product with id {req.id}: {str(e)}")

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
        
    def add_new_category(self, req: AddNewCategoryRequest):
        try:
            if self.db.query(Category).filter(Category.id == req.category).first():
                raise GenericException(reason=f"Category already exists with id: {req.category}")
            new_category = Category()
            new_category.id = req.category
            self.db.add(new_category)

            req.subcategories = list(set(req.subcategories))
            for subcat in req.subcategories:
                if not self.db.query(Subcategory).filter(Subcategory.id == subcat).first():
                    new_sub_category = Subcategory()
                    new_sub_category.id = subcat
                    self.db.add(new_sub_category)
                category_subcategory = CategorySubcategory()
                category_subcategory.category_id = req.category
                category_subcategory.subcategory_id = subcat
                self.db.add(category_subcategory)

            self.db.commit()
            return GenericResponse(
                status_code=status.HTTP_201_CREATED,
                msg=f"Category successfully added with id: {new_category.id}"
            )
        except GenericException:
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))
        
    def rename_category(self, req: RenameCategoryRequest):
        try:
            category = self.db.query(Category).filter(Category.id == req.category).first()
            if not category:
                raise GenericException(reason=f"Category not found with id: {req.category}")
            if self.db.query(Category).filter(Category.id == req.new_name).first():
                raise GenericException(reason=f"Category already exists with id: {req.new_name}")

            category.id = req.new_name
            self.db.commit()

            return GenericResponse(
                status_code=status.HTTP_200_OK,
                msg=f"Category successfully renamed to: {req.new_name}"
            )
        except GenericException:
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))
        
    def rename_subcategory(self, req: RenameSubcategoryRequest):
        try:
            subcategory = self.db.query(Subcategory).filter(Subcategory.id == req.subcategory).first()
            if not subcategory:
                raise GenericException(reason=f"Subcategory not found with id: {req.subcategory}")
            if self.db.query(Subcategory).filter(Subcategory.id == req.new_name).first():
                raise GenericException(reason=f"Subcategory already exists with id: {req.new_name}")
            subcategory.id = req.new_name
            self.db.commit()

            return GenericResponse(
                status_code=status.HTTP_200_OK,
                msg=f"Subcategory successfully renamed to: {req.new_name}"
            )
        except GenericException:
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))
    
    def edit_category(self, req: EditCategoryRequest):
        try:
            category = self.db.query(Category).filter(Category.id == req.category).first()
            if not category:
                raise GenericException(reason=f"Category not found with id: {req.category}")

            existing_subcategories = self.db.query(CategorySubcategory).filter(CategorySubcategory.category_id == req.category).all()
            existing_subcat_ids = {subcat.subcategory_id for subcat in existing_subcategories}
            new_subcat_ids = set(req.subcategories)
            to_add = new_subcat_ids - existing_subcat_ids
            to_remove = existing_subcat_ids - new_subcat_ids
            for subcat_id in to_add:
                if not self.db.query(Subcategory).filter(Subcategory.id == subcat_id).first():
                    new_sub_category = Subcategory()
                    new_sub_category.id = subcat_id
                    self.db.add(new_sub_category)
                category_subcategory = CategorySubcategory()
                category_subcategory.category_id = req.category
                category_subcategory.subcategory_id = subcat_id
                self.db.add(category_subcategory)

            for subcat_id in to_remove:
                product = self.__check_if_any_product_belongs_to_subcategory(subcat_id)
                if product is not None:
                    raise GenericException(reason=f"Cannot remove subcategory with id: {subcat_id} as product id: {product.id} belong to this subcategory")
                
                cat_related_to_subcat = self.db.query(CategorySubcategory).filter(
                    (CategorySubcategory.category_id == req.category) & 
                    (CategorySubcategory.subcategory_id == subcat_id)
                ).first()
                if cat_related_to_subcat:
                    self.db.delete(cat_related_to_subcat)
                    if not self.__check_if_subcategory_belongs_to_any_other_category(req.category, subcat_id):
                        subcat_to_delete = self.db.query(Subcategory).filter(Subcategory.id == subcat_id).first()
                        if subcat_to_delete:
                            self.db.delete(subcat_to_delete)
            
            self.db.commit()
            return GenericResponse(
                status_code=status.HTTP_200_OK,
                msg=f"Category successfully updated with id: {category.id}"
            )
        except GenericException:
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))
        
    def delete_category(self, req: DeleteCategoryRequest):
        try:
            category = self.db.query(Category).filter(Category.id == req.category).first()
            if not category:
                raise GenericException(reason=f"Category not found with id: {req.category}")
            
            product = self.__check_if_any_product_belongs_to_category(req.category)
            if product is not None:
                raise GenericException(reason=f"Cannot delete category with id: {req.category} as product id: {product.id} belong to this category")

            subcategories = self.db.query(CategorySubcategory).filter(CategorySubcategory.category_id == req.category).all()
            for subcat in subcategories:
                product = self.__check_if_any_product_belongs_to_subcategory(subcat.subcategory_id)
                if product is not None:
                    raise GenericException(reason=f"Cannot delete category with id: {req.category} and subcategory with id: {subcat.subcategory_id} as product id: {product.id} belong to this subcategory")

                cats_related_to_subcat = self.db.query(CategorySubcategory).filter(CategorySubcategory.category_id == req.category and CategorySubcategory.subcategory_id == subcat.subcategory_id).first()
                if cats_related_to_subcat:
                    self.db.delete(cats_related_to_subcat)
                    self.db.commit()
                if not self.__check_if_subcategory_belongs_to_any_other_category(req.category, subcat.subcategory_id):
                    subcat_to_delete = self.db.query(Subcategory).filter(Subcategory.id == subcat.subcategory_id).first()
                    if subcat_to_delete:
                        self.db.delete(subcat_to_delete)

            self.db.delete(category)
            self.db.commit()
            return GenericResponse(
                status_code=status.HTTP_200_OK,
                msg=f"Category successfully deleted with id: {req.category}"
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