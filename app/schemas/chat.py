from pydantic import BaseModel

class ChatOut(BaseModel):
	id: int
	username: str

	class Config:
		from_attributes = True
