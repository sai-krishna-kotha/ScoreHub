from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.db.base import Base

class TeamPlayer(Base):
    __tablename__ = "team_players"

    id = Column(Integer, primary_key=True)

    team_id = Column(Integer, ForeignKey("teams.id"))
    player_id = Column(Integer, ForeignKey("players.id"))
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))

    __table_args__ = (
        UniqueConstraint('player_id', 'tournament_id', name='unique_player_per_tournament'),
    )