from sqlalchemy import Column, Integer, ForeignKey
from ..db.session import Base
from sqlalchemy.orm import relationship

class CartProducts(Base):
    __tablename__ = "cart_products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    # products = relationship("Product", back_populates="cart_products")
    # carts = relationship("Cart", back_populates="cart_products")