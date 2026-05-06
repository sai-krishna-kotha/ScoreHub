from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.player import Player
from app.models.player_sport import PlayerSport
from app.core.security import get_current_user

router = APIRouter()

@router.get("/search")
def search_users(
    email: str = Query(..., min_length=2),
    sport_id: int = Query(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    
    users = (
        db.query(User)
        .select_from(PlayerSport)
        .join(Player, Player.id == PlayerSport.player_id)
        .join(User, User.id == Player.user_id)
        .filter(
            PlayerSport.sport_id == sport_id,
            User.email.ilike(f"%{email}%")
        )
        .limit(10)
        .all()
    )

    return [
        {
            "id": u.id,
            "email": u.email,
            "name": u.name
        }
        for u in users
    ]