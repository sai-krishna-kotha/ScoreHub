from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from app.db.base import Base

class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    sport_id = Column(Integer, ForeignKey("sports.id"))
    organizer_id = Column(Integer, ForeignKey("users.id"))

    city = Column(String)
    venue = Column(String)

    format = Column(String)
    max_teams = Column(Integer)

    sport_config = Column(JSON)