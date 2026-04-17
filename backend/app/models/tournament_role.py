from sqlalchemy import Column, Integer, ForeignKey, String, UniqueConstraint
from app.db.base import Base

class TournamentRole(Base):
    __tablename__ = "tournament_roles"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))

    role = Column(String)  # organizer, admin, scorer, viewer

    __table_args__ = (
        UniqueConstraint('user_id', 'tournament_id', name='unique_user_tournament'),
    )