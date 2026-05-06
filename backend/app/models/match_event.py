from sqlalchemy import Column, Integer, ForeignKey, String, JSON
from datetime import datetime
from app.db.base import Base

class MatchEvent(Base):
    __tablename__ = "match_events"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"))
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="CASCADE"))
    phase_id = Column(Integer)
    event_type = Column(String)
    payload = Column(JSON)
    timestamp = Column(String, default=str(datetime.utcnow()))