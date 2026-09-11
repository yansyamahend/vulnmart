from sqlalchemy import Column, ForeignKey, Integer, String

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    currency = Column(String, nullable=False, default="IDR")
    stock = Column(Integer, nullable=False, default=0)
    image = Column(String, nullable=True)