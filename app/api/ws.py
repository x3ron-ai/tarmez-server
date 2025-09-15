from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import jwt, JWTError
from app.core.config import settings
from app.models.user import User
from app.db.session import SessionLocal
from app.schemas.message import MessageOut

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active.setdefault(user_id, []).append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active:
            self.active[user_id] = [
                ws for ws in self.active[user_id] if ws != websocket
            ]
            if not self.active[user_id]:
                del self.active[user_id]

    async def send_to_user(self, user_id: int, message: dict):
        if user_id not in self.active:
            return
        disconnected = []
        for ws in self.active[user_id]:
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(user_id, ws)


manager = ConnectionManager()


async def get_current_user_ws(token: str) -> User | None:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id: str | None = payload.get("sub")
        if not user_id:
            return None
        with SessionLocal() as db:
            return db.query(User).filter(User.id == int(user_id)).first()
    except JWTError:
        return None


@router.websocket("/messages")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    user = await get_current_user_ws(token)
    if not user:
        await websocket.close(code=4002, reason="Invalid token")
        return

    await manager.connect(user.id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user.id, websocket)
    except Exception:
        manager.disconnect(user.id, websocket)
        try:
            await websocket.close()
        except RuntimeError:
            pass
