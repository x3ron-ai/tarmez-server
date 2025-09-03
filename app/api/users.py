from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, Token, TokenData, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_user_by_username(db: Session, username: str) -> User | None:
	return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str) -> User | None:
	user = get_user_by_username(db, username)
	if not user:
		return None
	if not verify_password(password, user.hashed_password):
		return None
	return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)
	try:
		payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
		user_id: str | None = payload.get("sub")
		if user_id is None:
			raise credentials_exception
		token_data = TokenData(sub=user_id)
	except JWTError:
		raise credentials_exception
	user = db.query(User).filter(User.id == int(token_data.sub)).first()
	if user is None:
		raise credentials_exception
	return user

@router.post("/register", response_model=UserOut, status_code=201)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
	exists = get_user_by_username(db, payload.username)
	if exists:
		raise HTTPException(status_code=400, detail="User with same username already exists")
	user = User(
		username=payload.username,
		hashed_password=get_password_hash(payload.password)
	)
	db.add(user)
	db.commit()
	db.refresh(user)
	return user

@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
	user = authenticate_user(db, payload.username, payload.password)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password",
			headers={"WWW-Authenticate": "Bearer"},
		)
	access_token = create_access_token({"sub": str(user.id)})
	return Token(access_token=access_token)

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
	return current_user

@router.get("/search", response_model=list[UserOut])
def search_users(
	username: str,
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user),
	limit: int = 10
):
	users = (
		db.query(User)
		.filter(User.username.ilike(f"%{username}%"))
		.filter(User.id != current_user.id)
		.limit(limit)
		.all()
	)
	return users

