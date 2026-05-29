import os
import logging
import bcrypt

# Monkeypatch bcrypt for passlib incompatibility
if not hasattr(bcrypt, "__about__"):
    class BcryptAbout:
        def __init__(self, version):
            self.__version__ = version
    bcrypt.__about__ = BcryptAbout(bcrypt.__version__)

# Fix for "ValueError: password cannot be longer than 72 bytes" in passlib + bcrypt 4.0+
_original_hashpw = bcrypt.hashpw
def _patched_hashpw(password, salt):
    if isinstance(password, str):
        password = password.encode("utf-8")
    if len(password) > 72:
        password = password[:72]
    return _original_hashpw(password, salt)
bcrypt.hashpw = _patched_hashpw

# Force passlib to use this patched version
try:
    import passlib.handlers.bcrypt
    passlib.handlers.bcrypt._bcrypt = bcrypt
except ImportError:
    pass

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, UserRole



# Secret key to encode the JWT token
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey12345")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    # Let passlib handle encoding and truncation for bcrypt compatibility
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme), 
    token_query: Optional[str] = Query(None, alias="token"),
    db: Session = Depends(get_db)
):
    actual_token = token or token_query
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not actual_token:
        raise credentials_exception

    try:
        payload = jwt.decode(actual_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_role(roles: list[UserRole]):
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user
    return role_checker
