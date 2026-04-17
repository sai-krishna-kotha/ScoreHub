from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, match_id: int, websocket: WebSocket):
        await websocket.accept()

        if match_id not in self.active_connections:
            self.active_connections[match_id] = []

        self.active_connections[match_id].append(websocket)

    def disconnect(self, match_id: int, websocket: WebSocket):
        self.active_connections[match_id].remove(websocket)

    async def broadcast(self, match_id: int, message: dict):
        if match_id in self.active_connections:
            for connection in self.active_connections[match_id]:
                await connection.send_json(message)