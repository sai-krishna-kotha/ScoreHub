from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.tournament_role import TournamentRole

def check_role(db: Session, user_id: int, tournament_id: int, allowed_roles: list):

    role = db.query(TournamentRole).filter(
        TournamentRole.user_id == user_id,
        TournamentRole.tournament_id == tournament_id
    ).first()

    if not role or role.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Not authorized")