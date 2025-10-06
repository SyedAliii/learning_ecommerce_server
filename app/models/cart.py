from sqlalchemy import Column, Integer, ForeignKey
from app.db.session import Base
from sqlalchemy.orm import relationship

class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # user = relationship("User", back_populates="active_cart", foreign_keys=[user_id])
    # cart_products = relationship("CartProducts", back_populates="carts")