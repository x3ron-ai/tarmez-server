from fastapi import APIRouter, WebSocket, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageOut
from jose import jwt, JWTError
from app.core.config import settings
import asyncio

router = APIRouter()


class ConnectionManager:
	def __init__(self):
		self.active_connections: dict[int, WebSocket] = {}

	async def connect(self, user_id: int, websocket: WebSocket):
		await websocket.accept()
		self.active_connections[user_id] = websocket

	def disconnect(self, user_id: int):
		if user_id in self.active_connections:
			del self.active_connections[user_id]

	async def send_message(self, user_id: int, message: dict):
		if user_id in self.active_connections:
			await self.active_connections[user_id].send_json(message)


manager = ConnectionManager()


async def get_current_user_ws(token: str) -> User:
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)
	try:
		payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
		user_id: str | None = payload.get("sub")
		if user_id is None:
			raise credentials_exception

		with SessionLocal() as db:
			user = db.query(User).filter(User.id == int(user_id)).first()
			if user is None:
				raise credentials_exception
			return user

	except JWTError:
		raise credentials_exception


@router.websocket("/messages")
async def websocket_endpoint(websocket: WebSocket):
	token = websocket.query_params.get("token")
	if not token:
		await websocket.close(code=4001, reason="Missing token")
		return

	try:
		user = await get_current_user_ws(token)
	except HTTPException:
		await websocket.close(code=4002, reason="Invalid token")
		return

	await manager.connect(user.id, websocket)

	with SessionLocal() as db:
		last_message = (
			db.query(Message)
			.filter((Message.sender_id == user.id) | (Message.receiver_id == user.id))
			.order_by(Message.id.desc())
			.first()
		)
		last_message_id = last_message.id if last_message else 0

	try:
		while True:
			with SessionLocal() as db:
				new_messages = (
					db.query(Message)
					.filter(
						Message.id > last_message_id,
						((Message.sender_id == user.id) | (Message.receiver_id == user.id))
					)
					.order_by(Message.created_at.asc())
					.all()
				)

				for msg in new_messages:
					last_message_id = max(last_message_id, msg.id)
					message_out = MessageOut(
						id=msg.id,
						content=msg.content,
						sender=msg.sender,
						receiver=msg.receiver,
						created_at=msg.created_at
					)
					await websocket.send_json(message_out.model_dump(mode="json"))

			await asyncio.sleep(settings.longpoll_interval)

	except Exception as e:
		print(f"WebSocket error: {e}")
	finally:
		manager.disconnect(user.id)
		try:
			await websocket.close()
		except RuntimeError:
			pass
