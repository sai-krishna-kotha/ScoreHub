from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.permissions import check_role
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.player import Player
from app.models.team_player import TeamPlayer
from app.schemas.player import PlayerCreate, AddPlayerToTeam

router = APIRouter()


@router.post("/")
def create_player(data: PlayerCreate, db: Session = Depends(get_db)):
    player = Player(user_id=data.user_id)
    db.add(player)
    db.commit()
    db.refresh(player)
    return player

@router.post("/add-to-team")
def add_player_to_team(
    data: AddPlayerToTeam, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
    ):

    check_role(db, user_id, data.tournament_id, ["organizer", "admin"])

    
    # check if already exists in tournament
    existing = db.query(TeamPlayer).filter(
        TeamPlayer.player_id == data.player_id,
        TeamPlayer.tournament_id == data.tournament_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Player already assigned to a team in this tournament"
        )

    team_player = TeamPlayer(
        team_id=data.team_id,
        player_id=data.player_id,
        tournament_id=data.tournament_id
    )

    db.add(team_player)
    db.commit()

    return {"message": "Player added to team"}