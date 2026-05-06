from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.permissions import check_role
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.player import Player
from app.models.team_player import TeamPlayer
from app.models.team import Team
from app.models.tournament import Tournament
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

    # RBAC
    check_role(
        db,
        user_id,
        data.tournament_id,
        ["organizer", "admin"]
    )

    # Validate team
    team = db.query(Team).filter(
        Team.id == data.team_id
    ).first()

    if not team:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    # Validate player
    player = db.query(Player).filter(
        Player.id == data.player_id
    ).first()

    if not player:
        raise HTTPException(
            status_code=404,
            detail="Player not found"
        )

    # Validate tournament
    tournament = db.query(Tournament).filter(
        Tournament.id == data.tournament_id
    ).first()

    if not tournament:
        raise HTTPException(
            status_code=404,
            detail="Tournament not found"
        )

    # Validate team belongs to tournament
    if team.tournament_id != data.tournament_id:
        raise HTTPException(
            status_code=400,
            detail="Team does not belong to this tournament"
        )

    # Validate player registered for sport
    player_sport = db.query(PlayerSport).filter(
        PlayerSport.player_id == player.id,
        PlayerSport.sport_id == tournament.sport_id
    ).first()

    if not player_sport:
        raise HTTPException(
            status_code=400,
            detail="Player is not registered for this sport"
        )

    # Prevent duplicate participation
    # One player → one team per tournament
    existing = db.query(TeamPlayer).filter(
        TeamPlayer.player_id == data.player_id,
        TeamPlayer.tournament_id == data.tournament_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Player already assigned to a team in this tournament"
        )

    # Add player to team
    team_player = TeamPlayer(
        team_id=data.team_id,
        player_id=data.player_id,
        tournament_id=data.tournament_id
    )

    db.add(team_player)
    db.commit()
    db.refresh(team_player)

    return {
        "message": "Player added to team successfully",
        "team_player_id": team_player.id
    }

@router.delete("/remove-from-team")
def remove_player_from_team(
    data: AddPlayerToTeam,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):

    # RBAC
    check_role(
        db,
        user_id,
        data.tournament_id,
        ["organizer", "admin"]
    )
    # Find team participation
    team_player = db.query(TeamPlayer).filter(
        TeamPlayer.player_id == data.player_id,
        TeamPlayer.team_id == data.team_id,
        TeamPlayer.tournament_id == data.tournament_id
    ).first()

    if not team_player:
        raise HTTPException(
            status_code=404,
            detail="Player is not part of this team"
        )

    # Remove ONLY team participation
    db.delete(team_player)
    db.commit()

    return {
        "message": "Player removed from team successfully"
    }