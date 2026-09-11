from sqlalchemy import Boolean, Column, Integer, String

from app.database import Base


class H5Challenge(Base):
    __tablename__ = "h5_challenges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    completed = Column(Boolean, nullable=False, default=False)
    flag = Column(String, nullable=False)