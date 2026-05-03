from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.models import *
from app.api import auth, team, player, tournament, match, event, ws, role
from fastapi import WebSocket, WebSocketDisconnect
from app.utils.connection_manager import ConnectionManager

manager = ConnectionManager()

app = FastAPI(title="Live Score System")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(team.router, prefix="/teams", tags=["Teams"])
app.include_router(player.router, prefix="/players", tags=["Players"])
app.include_router(tournament.router, prefix="/tournaments", tags=["Tournaments"])
app.include_router(match.router, prefix="/matches", tags=["Matches"])
app.include_router(event.router, prefix="/events", tags=["Events"])
app.include_router(ws.router)
app.include_router(role.router, prefix="/roles", tags=["Roles"])

@app.get("/")
def root():
    return {"message": "API running"}