from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.tournament_role import TournamentRole
from app.models.tournament import Tournament
from app.core.security import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/assign")
def assign_role(
    tournament_id: int,
    user_id_to_assign: int,
    role: str,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):

    # Check current user is organizer
    existing = db.query(TournamentRole).filter(
        TournamentRole.user_id == current_user,
        TournamentRole.tournament_id == tournament_id,
        TournamentRole.role == "organizer"
    ).first()

    if not existing:
        raise HTTPException(status_code=403, detail="Only organizer can assign roles")

    # Create role
    new_role = TournamentRole(
        user_id=user_id_to_assign,
        tournament_id=tournament_id,
        role=role
    )

    db.add(new_role)
    db.commit()

    return {"message": "Role assigned"}