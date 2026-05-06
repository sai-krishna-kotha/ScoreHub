from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.utils.permissions import check_role
from app.models.tournament import Tournament
from app.db.session import get_db
from app.models.match import Match
from app.models.team import Team
from app.schemas.match import MatchCreate
from app.models.sport import Sport
from app.models.match_phase import MatchPhase

router = APIRouter()


@router.post("/")
def create_match(
    data: MatchCreate,
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

    # Validate tournament
    tournament = db.query(Tournament).filter(
        Tournament.id == data.tournament_id
    ).first()

    if not tournament:
        raise HTTPException(
            status_code=404,
            detail="Tournament not found"
        )

    # Validate teams
    teams = db.query(Team).filter(
        Team.id.in_([data.team_a_id, data.team_b_id])
    ).all()

    if len(teams) != 2:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    # safer mapping
    teams_map = {team.id: team for team in teams}

    team_a = teams_map.get(data.team_a_id)
    team_b = teams_map.get(data.team_b_id)

    # Prevent same team
    if data.team_a_id == data.team_b_id:
        raise HTTPException(
            status_code=400,
            detail="A team cannot play against itself"
        )

    # Validate tournament ownership
    if (
        team_a.tournament_id != data.tournament_id
        or team_b.tournament_id != data.tournament_id
    ):
        raise HTTPException(
            status_code=400,
            detail="Teams must belong to same tournament"
        )

    # Prevent duplicate matches
    existing_match = db.query(Match).filter(
        Match.tournament_id == data.tournament_id,
        (
            (
                (Match.team_a_id == data.team_a_id) &
                (Match.team_b_id == data.team_b_id)
            )
            |
            (
                (Match.team_a_id == data.team_b_id) &
                (Match.team_b_id == data.team_a_id)
            )
        )
    ).first()

    if existing_match:
        raise HTTPException(
            status_code=400,
            detail="Match already exists between these teams"
        )

    # Validate sport config
    sport = db.query(Sport).filter(
        Sport.id == tournament.sport_id
    ).first()

    if not sport:
        raise HTTPException(
            status_code=404,
            detail="Sport not found"
        )

    sport_config = sport.config or {}

    num_phases = sport_config.get("phases")
    phase_type = sport_config.get("phase_type")

    if not num_phases or not phase_type:
        raise HTTPException(
            status_code=500,
            detail="Invalid sport configuration"
        )

    # Create match
    match = Match(
        tournament_id=data.tournament_id,
        team_a_id=data.team_a_id,
        team_b_id=data.team_b_id,
        status="scheduled"
    )

    db.add(match)
    db.flush()  # match.id available without commit

    # Create phases
    phases = [
        MatchPhase(
            match_id=match.id,
            phase_number=i + 1,
            phase_type=phase_type,
            status="pending"
        )
        for i in range(num_phases)
    ]

    db.add_all(phases)

    # Commit transaction
    db.commit()

    db.refresh(match)

    return {
        "message": "Match created successfully",
        "match": {
            "id": match.id,
            "tournament_id": match.tournament_id,
            "team_a_id": match.team_a_id,
            "team_b_id": match.team_b_id,
            "status": match.status
        }
    }

@router.put("/{match_id}/start")
def start_match(
    match_id: int, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
    ):
    
    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status != "scheduled":
        raise HTTPException(status_code=400, detail="Match cannot be started")
    
    tournament = db.query(Tournament).filter(
        Tournament.id == match.tournament_id
    ).first()

    # 🔥 RBAC check
    check_role(db, user_id, tournament.id, ["organizer", "admin"])
    match.status = "live"
    db.commit()

    return {"message": "Match started"}

@router.put("/{match_id}/complete")
def complete_match(
    match_id: int, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
    ):

    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status != "live":
        raise HTTPException(status_code=400, detail="Match is not live")
    
    tournament = db.query(Tournament).filter(
        Tournament.id == match.tournament_id
    ).first()

    check_role(db, user_id, tournament.id, ["organizer", "admin"])

    match.status = "completed"
    db.commit()

    return {"message": "Match completed"}

@router.get("/")
def get_matches(db: Session = Depends(get_db)):
    return db.query(Match).all()