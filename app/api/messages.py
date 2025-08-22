import asyncio
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageOut
from app.api.users import get_current_user
from app.models.user import User
from app.core.config import settings

router = APIRouter()

@router.post("/", response_model=MessageOut, status_code=201)
def create_message(
	payload: MessageCreate,
	db: Session = Depends(get_db),
	user: User = Depends(get_current_user)
):
	msg = Message(
		content=payload.content,
		sender_id=user.id,
		receiver_id=payload.receiver_id
	)
	db.add(msg)
	db.commit()
	db.refresh(msg)
	return msg

@router.get("/updates", response_model=list[MessageOut])
async def get_updates(
	last_message_id: int = 0,
	timeout: int = settings.longpoll_timeout,
	db: Session = Depends(get_db),
	user = Depends(get_current_user)
):
	interval = settings.longpoll_interval
	for _ in range(timeout):
		new_messages = (
			db.query(Message)
			.filter(
				Message.receiver_id == user.id,
				Message.id > last_message_id
			)
			.order_by(Message.created_at.asc())
			.all()
		)
		if new_messages:
			return new_messages
		await asyncio.sleep(interval)

	return []