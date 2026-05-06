from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.security import hash_password, verify_password, create_access_token
from app.models.player import Player
router = APIRouter()


@router.post("/signup")
def signup(data: UserCreate, db: Session = Depends(get_db)):

    # Check existing email
    existing_user = db.query(User).filter(
        User.email == data.email
    ).first()

    # User already fully registered
    if existing_user and existing_user.password is not None:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # User exists as unclaimed account
    if existing_user and existing_user.password is None:

        existing_user.name = data.name
        existing_user.password = hash_password(data.password)
        existing_user.is_active = True

        db.commit()
        db.refresh(existing_user)

        return {
            "message": "Account claimed successfully",
            "user": {
                "id": existing_user.id,
                "email": existing_user.email,
                "name": existing_user.name
            }
        }

    # Completely new signup
    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        is_active=True
    )

    db.add(user)
    db.flush()

    # Create player profile automatically
    player = Player(user_id=user.id)

    db.add(player)

    db.commit()

    return {
        "message": "User created successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        },
        "player_id": player.id
    }


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user.password is None:
        raise HTTPException(
            status_code=403,
            detail="Account not activated. Please set your password."
        )
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"user_id": user.id})

    return {"access_token": token}