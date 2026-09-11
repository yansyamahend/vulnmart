from sqlalchemy import Column, Integer, String

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)

    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    bio = Column(String, nullable=True)

    account_number = Column(String, unique=True, nullable=False, index=True)