from sqlalchemy import Column, Integer, String, Enum as AlchemyEnum, ForeignKey
from app.db.session import Base
from sqlalchemy.orm import relationship
import enum

class ProductStatus(enum.Enum):
    AVAILABLE = "available"
    DELISTED = "delisted"

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True)
    title = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    category_id = Column(String, ForeignKey("categories.id"), nullable=False)
    subcategory_id = Column(String, ForeignKey("subcategories.id"), nullable=False)
    status = Column(AlchemyEnum(ProductStatus), nullable=False)
    url_slug = Column(String, unique=True, nullable=False)

    images = relationship("ProductImage", back_populates="product")
    category = relationship("Category", back_populates="products")
    subcategory = relationship("Subcategory", back_populates="products")
    # cart_products = relationship("CartProducts", back_populates="products")