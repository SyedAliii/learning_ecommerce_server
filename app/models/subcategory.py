from sqlalchemy import Column, Integer, String, Enum as AlchemyEnum
from app.db.session import Base
from sqlalchemy.orm import relationship
import enum

class Subcategory(Base):
    __tablename__ = "subcategories"

    id = Column(String, unique=True, primary_key=True)

    categories_subcategories = relationship("CategorySubcategory", back_populates="subcategories")
    products = relationship("Product", back_populates="subcategory")