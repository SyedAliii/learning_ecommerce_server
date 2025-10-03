from sqlalchemy import Column, Integer, String, Enum as AlchemyEnum
from ..db.session import Base
from sqlalchemy.orm import relationship
import enum

class ProductStatus(enum.Enum):
    AVAILABLE = "available"
    DELISTED = "delisted"

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    discount = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    subcategory = Column(String, nullable=False)
    status = Column(AlchemyEnum(ProductStatus), nullable=False)

    # images = relationship("ProductImage", back_populates="product")
    # cart_products = relationship("CartProducts", back_populates="products")