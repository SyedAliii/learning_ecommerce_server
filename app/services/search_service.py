from typing import List
from app.models.product_image import ProductImage
from app.schemas.generic import GenericResponse
from app.schemas.product import ProductBaseModel
from app.schemas.search import SearchResponse
from app.models.product import Product, ProductStatus
from sqlalchemy.orm import Session
from app.core.exceptions.exception_main import GenericException
from app.core.config import settings
from rapidfuzz import fuzz, process
from fastapi import status

from app.utils import str_helper

class SearchService:
    def __init__(self, db: Session):
        self.db = db

    def __fuzzy_search(self, query: str):
        products = self.db.query(Product).all()
        product_id_title = [(product.id, product.title) for product in products]
        fuzzy_results = process.extract(query, [title for _, title in product_id_title], scorer=fuzz.partial_ratio)
        # return [products[i] for i, score in fuzzy_results if score > settings.FUZZY_SEARCH_THRESHOLD]
        return

    def search(self, query: str):
        try:
            if not query:
                raise GenericException(reason="Search query is empty")

            products = self.db.query(Product).filter(Product.title.like(f"%{query}%")).filter(Product.status == ProductStatus.AVAILABLE).all()
            if not products:
                return GenericResponse(
                    status_code=status.HTTP_204_NO_CONTENT,
                    msg="No products found"
                )
            
            product_list = []
            for product in products:
                product_data = product.__dict__
                product_images : List[ProductImage] = product.images
                url_slug = f"{str_helper.slugify(product.category_id)}/{str_helper.slugify(product.subcategory_id)}/{str_helper.slugify(product.title)}/{product.id}"
                product_model = ProductBaseModel(**product_data, url_slug=url_slug, product_img_urls=[img.url for img in product_images])
                product_list.append(product_model)

            return SearchResponse(
                status_code=status.HTTP_200_OK,
                msg="Products found",
                products=product_list
            )
        except GenericException:
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))