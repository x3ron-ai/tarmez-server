from pydantic import BaseModel, ConfigDict
from .user import UserOut
from datetime import datetime

class MessageBase(BaseModel):
	content: str

class MessageCreate(MessageBase):
	receiver_id: int

class MessageOut(MessageBase):
	id: int
	sender: UserOut
	receiver: UserOut
	created_at: datetime
	
	model_config = ConfigDict(from_attributes=True)