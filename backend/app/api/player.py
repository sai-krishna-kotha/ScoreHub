from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.permissions import check_role
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.player import Player
from app.models.team_player import TeamPlayer
from app.schemas.player import PlayerCreate, AddPlayerToTeam
from app.schemas.create_user import CreateUserByAdmin
from app.models.user import User
from app.models.player_sport import PlayerSport

router = APIRouter()

@router.post("/create-by-admin")
def create_user_by_admin(
    data: CreateUserByAdmin,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    # RBAC
    check_role(db, user_id, data.tournament_id, ["organizer", "admin"])

    # Check existing user
    existing = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing:
        player = db.query(Player).filter(
            Player.user_id == existing.id
        ).first()

        # Create player if missing
        if not player:
            player = Player(user_id=existing.id)
            db.add(player)
            db.flush()

        # Check player-sport relation
        existing_relation = db.query(PlayerSport).filter(
            PlayerSport.player_id == player.id,
            PlayerSport.sport_id == data.sport_id
        ).first()

        # Create relation if missing
        if not existing_relation:
            player_sport = PlayerSport(
                player_id=player.id,
                sport_id=data.sport_id
            )

            db.add(player_sport)

        db.commit()

        return {
            "message": "Existing user linked successfully",
            "user": {
                "id": existing.id,
                "email": existing.email,
                "name": existing.name
            },
            "player_id": player.id
        }
    user = User(
        email=data.email,
        name=data.name,
        password=None,
        is_active=False
    )

    db.add(user)
    db.flush()

    # Create player
    player = Player(user_id=user.id)

    db.add(player)
    db.flush()

    # Create player-sport relation
    player_sport = PlayerSport(
        player_id=player.id,
        sport_id=data.sport_id
    )

    db.add(player_sport)

    db.commit()

    return {
        "message": "User created successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        },
        "player_id": player.id
    }
    

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