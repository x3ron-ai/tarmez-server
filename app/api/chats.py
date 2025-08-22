from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, case
from app.db.session import get_db
from app.models.message import Message
from app.models.user import User
from app.api.users import get_current_user
from app.schemas.message import MessageOut

router = APIRouter()

@router.get("/", response_model=list[dict])
def list_chats(
	db: Session = Depends(get_db),
	user: User = Depends(get_current_user)
):
	subq = (
		db.query(
			case(
				[(Message.sender_id == user.id, Message.receiver_id)],
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
		.filter(User.id.in_(subq))
		.filter(User.id != user.id)
		.all()
	)

	return [{"id": u.id, "username": u.username} for u in partners]


@router.get("/{other_user_id}/messages", response_model=list[MessageOut])
def get_chat_messages(
	other_user_id: int,
	skip: int = 0,
	limit: int = 50,
	db: Session = Depends(get_db),
	user: User = Depends(get_current_user)
):
	return (
		db.query(Message)
		.filter(
			or_(
				and_(Message.sender_id == user.id, Message.receiver_id == other_user_id),
				and_(Message.sender_id == other_user_id, Message.receiver_id == user.id)
			)
		)
		.order_by(Message.created_at.asc())
		.offset(skip)
		.limit(limit)
		.all()
	)