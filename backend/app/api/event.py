from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.match_event import MatchEvent
from app.models.match import Match
from app.schemas.event import EventCreate
from app.api.ws import manager
from app.utils.permissions import check_role
from app.core.security import get_current_user
from app.models.tournament import Tournament
from app.services.scoring.factory import get_engine
from app.models.tournament import Tournament
from app.models.sport import Sport

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
async def add_event(
    data: EventCreate, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
    ):

    match = db.query(Match).filter(Match.id == data.match_id).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status != "live":
        raise HTTPException(status_code=400, detail="Match is not live")
    print(f"match.tournament_id :{match.tournament_id} and match.id :{match.id}")
    tournament = db.query(Tournament).filter(
        Tournament.id == match.tournament_id
    ).first()
    
    check_role(db, user_id, tournament.id, ["organizer", "scorer"])
    
    event = MatchEvent(
        match_id=data.match_id,
        event_type=data.event_type,
        payload=data.payload
    )

    db.add(event)
    db.commit()

    # 🔥 Calculate updated score
    events = db.query(MatchEvent).filter(
        MatchEvent.match_id == data.match_id
    ).all()

    # score = calculate_cricket_score(events)


    sport = db.query(Sport).filter(
        Sport.id == tournament.sport_id
    ).first()

    engine = get_engine(sport.name)
    score = engine.calculate_score(events)
    
    # 🔥 Broadcast to all clients
    await manager.broadcast(data.match_id, {
        "type": "score_update",
        "data": score
    })

    return {"message": "Event added"}

def calculate_cricket_score(events):
    runs = 0
    wickets = 0
    balls = 0

    for e in events:
        if e.event_type == "BALL":
            runs += e.payload.get("runs", 0)
            balls += 1

        elif e.event_type == "WICKET":
            wickets += 1
            balls += 1

    overs = f"{balls//6}.{balls%6}"

    return {
        "runs": runs,
        "wickets": wickets,
        "overs": overs
    }


def calculate_football_score(events):
    goals = 0

    for e in events:
        if e.event_type == "GOAL":
            goals += 1

    return {"goals": goals}


@router.get("/{match_id}/score")
def get_score(match_id: int, db: Session = Depends(get_db)):

    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    events = db.query(MatchEvent).filter(
        MatchEvent.match_id == match_id
    ).all()

    # basic logic (we improve later)
    if match.tournament_id == 2:  # assume cricket for now
        return calculate_cricket_score(events)
    else:
        return calculate_football_score(events)