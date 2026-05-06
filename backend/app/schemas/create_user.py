from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

class CreateUserByAdmin(BaseModel):
    email: EmailStr
    name: str | None = "Player"
    tournament_id: int
    sport_id: int