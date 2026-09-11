from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint

from app.database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    balance = Column(Integer, nullable=False, default=0)
    currency = Column(String, nullable=False, default="IDR")

    __table_args__ = (
        UniqueConstraint("user_id", "currency", name="uq_user_currency"),
    )