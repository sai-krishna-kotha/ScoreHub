from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.tournament_role import TournamentRole
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.tournament import Tournament
from app.models.sport import Sport
from app.schemas.tournament import TournamentCreate, TournamentResponse

router = APIRouter()


@router.post("/", response_model=TournamentResponse)
def create_tournament(
    data: TournamentCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    existing = db.query(Tournament).filter(
        Tournament.name == data.name,
        Tournament.organizer_id == user_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Tournament already exists")
    
    tournament = Tournament(
        name=data.name,
        sport_id=data.sport_id,
        organizer_id=user_id,
        city=data.city,
        venue=data.venue,
        format=data.format,
        max_teams=data.max_teams,
        sport_config=data.sport_config
    )
    
    db.add(tournament)
    db.commit()
    db.refresh(tournament)
    
    # 🔥 Assign organizer role
    role = TournamentRole(
        user_id=user_id,
        tournament_id=tournament.id,
        role="organizer"
    )

    db.add(role)
    db.commit()
    
    return tournament

@router.get("/")
def get_tournaments(db: Session = Depends(get_db)):
    tournaments = db.query(Tournament).all()
    return tournaments

@router.get("/{tournament_id}")
def get_tournament(tournament_id: int, db: Session = Depends(get_db)):
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()

    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    return tournament