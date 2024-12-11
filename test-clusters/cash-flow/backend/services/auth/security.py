from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from models import User
import crud

from app_logging import AppLogger, config
logger = AppLogger('AuthService')

# Password context for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against the hashed password stored in the database.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a plain text password before storing it in the database.
    """
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate the user by verifying their username and password.
    """
    logger.debug ("Authenticating user")
    logger.debug (f'username: {username}, password: {password}')

    user = crud.get_user_by_username(username)

    if not user:
        return None

    if not verify_password(password, get_password_hash(password)):
        return None

    return user