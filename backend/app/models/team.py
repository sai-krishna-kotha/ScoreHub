from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))