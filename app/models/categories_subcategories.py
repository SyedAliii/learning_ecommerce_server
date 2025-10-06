from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.session import Base
from sqlalchemy.orm import relationship
import enum

class CategorySubcategory(Base):
    __tablename__ = "categories_subcategories"

    id = Column(String, primary_key=True)
    category_id = Column(String, ForeignKey("categories.id"), nullable=False)
    subcategory_id = Column(String, ForeignKey("subcategories.id"), nullable=False)

    categories = relationship("Category", back_populates="categories_subcategories")
    subcategories = relationship("Subcategory", back_populates="categories_subcategories")