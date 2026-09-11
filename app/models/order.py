from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    total_amount = Column(Integer, nullable=False)
    currency = Column(String, nullable=False, default="IDR")
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    challenge_flag = Column(String, nullable=True)
    reference_code = Column(String, nullable=True)
    description = Column(String, nullable=True)