from sqlalchemy import Column, Integer, ForeignKey, String
from app.db.base import Base

class MatchPhase(Base):
    __tablename__ = "match_phases"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    phase_number = Column(Integer)
    phase_type = Column(String)  # innings / half / quarter
    status = Column(String, default="pending")