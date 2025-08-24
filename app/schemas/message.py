from pydantic import BaseModel, ConfigDict
from datetime import datetime

class MessageBase(BaseModel):
	content: str

class MessageCreate(MessageBase):
	receiver_id: int

class MessageOut(MessageBase):
	id: int
	sender_id: int
	receiver_id: int
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)