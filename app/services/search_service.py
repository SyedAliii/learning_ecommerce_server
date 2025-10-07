from app.schemas.generic import GenericResponse
from app.models.product import Product, ProductStatus
from sqlalchemy.orm import Session
from app.core.exceptions.exception_main import GenericException
from app.core.config import settings
from rapidfuzz import fuzz, process

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
            self.__fuzzy_search(query)
            return
            # if not query:
            #     raise GenericException(reason="Search query is empty")

            # products = self.db.query(Product).filter(Product.title.ilike(f"%{query}%")).all()
            # if not products:
            #     return GenericResponse(
            #         status_code=status.HTTP_204_NO_CONTENT,
            #         msg="No products found"
            #     )

            # return GenericResponse(
            #     status_code=status.HTTP_200_OK,
            #     msg="Products found",
            #     data=products
            # )
        except GenericException:
            raise
        except Exception as e:
            self.db.rollback()
            raise GenericException(reason=str(e))