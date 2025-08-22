from pydantic import BaseModel
from datetime import datetime

class MessageBase(BaseModel):
	content: str

class MessageCreate(MessageBase):
	pass

class MessageOut(MessageBase):
	id: int
	created_at: datetime
	user_id: int | None

	class Config:
		from_attributes = True