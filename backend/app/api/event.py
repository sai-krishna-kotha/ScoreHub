from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.match_event import MatchEvent
from app.models.match import Match
from app.schemas.event import EventCreate
from app.api.ws import manager
from app.utils.permissions import check_role
from app.core.security import get_current_user
from app.models.tournament import Tournament
from app.services.scoring.factory import get_engine
from app.models.sport import Sport
from app.models.match_phase import MatchPhase

router = APIRouter()


@router.post("/")
async def add_event(
    data: EventCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):

    # Validate match
    match = db.query(Match).filter(Match.id == data.match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status != "live":
        raise HTTPException(status_code=400, detail="Match is not live")

    # Get tournament
    tournament = db.query(Tournament).filter(
        Tournament.id == match.tournament_id
    ).first()

    # RBAC
    check_role(db, user_id, tournament.id, ["organizer", "scorer"])

    # 🔥 Validate phase
    phase = db.query(MatchPhase).filter(
        MatchPhase.id == data.phase_id,
        MatchPhase.match_id == data.match_id
    ).first()

    if not phase:
        raise HTTPException(status_code=400, detail="Invalid phase")

    # (optional for now)
    # if phase.status != "active":
    #     raise HTTPException(400, "Phase not active")

    # 🔥 Create event WITH phase_id
    event = MatchEvent(
        match_id=data.match_id,
        phase_id=data.phase_id,
        event_type=data.event_type,
        payload=data.payload
    )

    db.add(event)
    db.commit()

    # 🔥 Recalculate score
    events = db.query(MatchEvent).filter(
        MatchEvent.match_id == data.match_id
    ).all()

    sport = db.query(Sport).filter(
        Sport.id == tournament.sport_id
    ).first()

    engine = get_engine(sport.name)
    score = engine.calculate_score(events)

    # 🔥 Broadcast
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