from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=True)   # allow NULL
    name = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)