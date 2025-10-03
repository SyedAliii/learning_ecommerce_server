from sqlalchemy import Column, Integer, ForeignKey, Enum as AlchemyEnum
from ..db.session import Base
from sqlalchemy.orm import relationship
import enum

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subtotal = Column(Integer, nullable=False)
    tax = Column(Integer, nullable=False)
    shipping_fee = Column(Integer, nullable=False)
    grand_total = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)

    # user = relationship("User", back_populates="active_cart", foreign_keys=[user_id])
    # cart_products = relationship("CartProducts", back_populates="carts")