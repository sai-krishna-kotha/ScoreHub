from pydantic import BaseModel
from typing import Dict

class EventCreate(BaseModel):
    match_id: int
    team_id: int
    phase_id: int
    event_type: str
    payload: Dict