from sqlalchemy import Column, Integer, String, ForeignKey, Enum as AlchemyEnum
from app.db.session import Base
from sqlalchemy.orm import relationship
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    roles = Column(AlchemyEnum(UserRole), nullable=False)
    hashed_password = Column(String, nullable=False)
    active_cart_id = Column(Integer, ForeignKey("carts.id"), nullable=True)

    # active_cart = relationship("Cart", back_populates="user",
    #                 foreign_keys=[active_cart_id], uselist=False)
