from pydantic import BaseModel

class MatchCreate(BaseModel):
    tournament_id: int
    team_a_id: int
    team_b_id: int