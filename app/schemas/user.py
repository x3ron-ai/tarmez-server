from pydantic import BaseModel, constr

class UserBase(BaseModel):
	username: str

class UserCreate(UserBase):
	password: constr(min_length=8, max_length=128)

class UserLogin(UserBase):
	password: str

class UserOut(UserBase):
	id: int
	class Config:
		from_attributes = True

class Token(BaseModel):
	access_token: str
	token_type: str = "bearer"

class TokenData(BaseModel):
	sub: int | None = None
