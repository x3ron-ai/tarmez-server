from pydantic import BaseModel
from datetime import datetime

class MessageBase(BaseModel):
	content: str

class MessageCreate(MessageBase):
	receiver_id: int

class MessageOut(MessageBase):
	id: int
	created_at: datetime
	sender_id: int
	receiver_id: int

	class Config:
		from_attributes = True