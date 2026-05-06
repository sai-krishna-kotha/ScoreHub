from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter()

@router.get("/search")
def search_users(
    email: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    users = db.query(User).filter(
        User.email.ilike(f"%{email}%")
    ).limit(10).all()

    return [
        {
            "id": u.id,
            "email": u.email,
            "name": u.name
        }
        for u in users
    ]
    
