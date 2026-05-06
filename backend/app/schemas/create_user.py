from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

class CreateUserByAdmin(BaseModel):
    email: EmailStr
    name: str | None = None
    tournament_id: int