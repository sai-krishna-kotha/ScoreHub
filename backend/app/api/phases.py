from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from app.utils.permissions import check_role
from app.models.tournament import Tournament
from app.models.match import Match
from app.models.team import Team
from app.schemas.match import MatchCreate
from app.models.sport import Sport
from app.models.match_phase import MatchPhase

router = APIRouter()

@router.put("/phases/{phase_id}/start")
def start_phase(
    data: MatchPhase,
    phase_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
    ):
    check_role(db, user_id, data.tournament_id, ["organizer", "admin"])

    phase = db.query(MatchPhase).filter(MatchPhase.id == phase_id).first()

    if not phase:
        raise HTTPException(404, "Phase not found")

    # deactivate other phases
    db.query(MatchPhase).filter(
        MatchPhase.match_id == phase.match_id,
        MatchPhase.status == "active"
    ).update({"status": "completed"})

    phase.status = "active"
    db.commit()

    return {"message": "Phase started"}

def get_active_phase(db, match_id):
    return db.query(MatchPhase).filter(
        MatchPhase.match_id == match_id,
        MatchPhase.status == "active"
    ).first()