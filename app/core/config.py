from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
	secret_key: str = os.getenv("SECRET_KEY", "change_me")
	algorithm: str = os.getenv("ALGORITHM", "HS256")
	access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
	database_url: str = os.getenv("DATABASE_URL", "sqlite:///./test_db.sqlite3")
	
	longpoll_timeout: int = int(os.getenv("LONGPOLL_TIMEOUT", "15"))
	longpoll_interval: int = int(os.getenv("LONGPOLL_INTERVAL", "1"))
	default_search_limit: int = int(os.getenv("DEFAULT_SEARCH_LIMIT", "10"))
	default_message_limit: int = int(os.getenv("DEFAULT_MESSAGE_LIMIT", "50"))
	
	password_min_length: int = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
	password_max_length: int = int(os.getenv("PASSWORD_MAX_LENGTH", "128"))

settings = Settings()
