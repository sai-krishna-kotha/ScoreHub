from sqlalchemy import Column, Integer, ForeignKey, String
from app.db.base import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)

    tournament_id = Column(Integer, ForeignKey("tournaments.id"))

    team_a_id = Column(Integer, ForeignKey("teams.id"))
    team_b_id = Column(Integer, ForeignKey("teams.id"))

    status = Column(String)  # scheduled / live / completed