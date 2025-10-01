from sqlalchemy import Column, ForeignKey, Integer, String
from ..db.session import Base
from sqlalchemy.orm import relationship

class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String, nullable=False)
    # images = Column(Integer, ForeignKey("products.id"), nullable=False)

    # product = relationship("Product", back_populates="images")