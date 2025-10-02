from sqlalchemy import Column, Integer, String
from ..db.session import Base
from sqlalchemy.orm import relationship

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

    # images = relationship("ProductImage", back_populates="product")
    # cart_products = relationship("CartProducts", back_populates="products")