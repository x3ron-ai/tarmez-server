from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

if os.environ.get("TESTING"):
	database_url = "sqlite:///./test_db.sqlite3"
else:
	database_url = os.getenv("DATABASE_URL")

class Settings(BaseModel):
	secret_key: str = os.getenv("SECRET_KEY", "change_me")
	algorithm: str = os.getenv("ALGORITHM", "HS256")
	access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
	database_url: str = database_url
	longpoll_timeout: int = 15
	longpoll_interval: int = 1

settings = Settings()