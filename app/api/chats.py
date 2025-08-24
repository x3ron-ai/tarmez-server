from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import case, or_, select
from app.db.session import get_db
from app.models.message import Message
from app.models.user import User
from app.api.users import get_current_user

router = APIRouter()

@router.get("/", response_model=list[dict])
def list_chats(
	db: Session = Depends(get_db),
	user: User = Depends(get_current_user)
):
	subq = (
		db.query(
			case(
				(Message.sender_id == user.id, Message.receiver_id),
				else_=Message.sender_id
			).label("user_id")
		)
		.filter(
			or_(Message.sender_id == user.id, Message.receiver_id == user.id)
		)
		.subquery()
	)

	partners = (
		db.query(User.id, User.username)
		.filter(User.id.in_(select(subq.c.user_id)))
		.filter(User.id != user.id)
		.all()
	)

	return [{"id": u.id, "username": u.username} for u in partners]