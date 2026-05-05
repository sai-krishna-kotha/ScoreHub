from sqlalchemy import Column, Integer, String, JSON
from app.db.base import Base

class Sport(Base):
    __tablename__ = "sports"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    config = Column(JSON, nullable=True)