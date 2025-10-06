from sqlalchemy import Column, Integer, String, Enum as AlchemyEnum
from app.db.session import Base
from sqlalchemy.orm import relationship
import enum

class Category(Base):
    __tablename__ = "categories"

    id = Column(String, unique=True, primary_key=True)

    categories_subcategories = relationship("CategorySubcategory", back_populates="categories")
    products = relationship("Product", back_populates="category")