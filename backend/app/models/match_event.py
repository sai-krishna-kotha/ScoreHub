from sqlalchemy import Column, Integer, ForeignKey, String, JSON
from datetime import datetime
from app.db.base import Base

class MatchEvent(Base):
    __tablename__ = "match_events"

    id = Column(Integer, primary_key=True)

    match_id = Column(Integer, ForeignKey("matches.id"))

    event_type = Column(String)
    payload = Column(JSON)

    timestamp = Column(String, default=str(datetime.utcnow()))