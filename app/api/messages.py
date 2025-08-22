from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageOut
from app.api.users import get_current_user
from app.models.user import User

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
