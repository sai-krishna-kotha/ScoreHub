from pydantic import BaseModel

class PlayerCreate(BaseModel):
    user_id: int


class AddPlayerToTeam(BaseModel):
    player_id: int
    team_id: int
    tournament_id: int