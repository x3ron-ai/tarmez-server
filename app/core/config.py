from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
	secret_key: str = os.getenv("SECRET_KEY", "change_me")
	algorithm: str = os.getenv("ALGORITHM", "HS256")
	access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
	database_url: str = os.getenv("DATABASE_URL")

	longpoll_timeout: int = 15
	longpoll_interval: int = 1

settings = Settings()