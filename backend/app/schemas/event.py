from pydantic import BaseModel
from typing import Dict

class EventCreate(BaseModel):
    match_id: int
    event_type: str
    payload: Dict