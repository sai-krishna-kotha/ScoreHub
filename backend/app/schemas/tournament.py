from pydantic import BaseModel, ConfigDict
from typing import Dict

class TournamentCreate(BaseModel):
    name: str
    sport_id: int
    city: str
    venue: str
    format: str
    max_teams: int
    sport_config: Dict
    
class TournamentResponse(BaseModel):
    id: int
    name: str
    sport_id: int
    organizer_id: int
    city: str
    venue: str
    format: str
    max_teams: int
    sport_config: Dict

    model_config = ConfigDict(from_attributes=True)