from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.utils.permissions import check_role
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.team import Team
from app.schemas.team import TeamCreate

router = APIRouter()


@router.post("/")
def create_team(
    data: TeamCreate, 
    db: Session = Depends(get_db), 
    user_id: int = Depends(get_current_user)
    ):
    
    check_role(db, user_id, data.tournament_id, ["organizer", "admin"])
    
    team = Team(
        name=data.name,
        tournament_id=data.tournament_id
    )

    db.add(team)
    db.commit()
    db.refresh(team)
    return team