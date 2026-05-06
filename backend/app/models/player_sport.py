from sqlalchemy import Column, Integer, ForeignKey
from app.db.base import Base


class PlayerSport(Base):
    __tablename__ = "player_sports"

    id = Column(Integer, primary_key=True)

    player_id = Column(Integer, ForeignKey("players.id"))
    sport_id = Column(Integer, ForeignKey("sports.id"))