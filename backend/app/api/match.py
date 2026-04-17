from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.utils.permissions import check_role
from app.models.tournament import Tournament
from app.db.session import SessionLocal
from app.models.match import Match
from app.models.team import Team
from app.schemas.match import MatchCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def create_match(
    data: MatchCreate, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
    ):

    check_role(db, user_id, data.tournament_id, ["organizer", "admin"])
    
    # Validate teams exist
    team_a = db.query(Team).filter(Team.id == data.team_a_id).first()
    team_b = db.query(Team).filter(Team.id == data.team_b_id).first()

    if not team_a or not team_b:
        raise HTTPException(status_code=404, detail="Team not found")

    # Validate same tournament
    if team_a.tournament_id != data.tournament_id or team_b.tournament_id != data.tournament_id:
        raise HTTPException(status_code=400, detail="Teams must belong to same tournament")

    # Prevent same team vs itself
    if data.team_a_id == data.team_b_id:
        raise HTTPException(status_code=400, detail="A team cannot play against itself")

    match = Match(
        tournament_id=data.tournament_id,
        team_a_id=data.team_a_id,
        team_b_id=data.team_b_id,
        status="scheduled"
    )

    db.add(match)
    db.commit()
    db.refresh(match)

    return match

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