from sqlalchemy import Column, Integer, ForeignKey, Enum as AlchemyEnum
from ..db.session import Base
from sqlalchemy.orm import relationship
import enum

class OrderStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    status = Column(AlchemyEnum(OrderStatus), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)

    # user = relationship("User", back_populates="active_cart", foreign_keys=[user_id])
    # cart_products = relationship("CartProducts", back_populates="carts")