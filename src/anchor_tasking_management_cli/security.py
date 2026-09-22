# security.py
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
import os
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from . import database

#------ Passwords ------
_ph = PasswordHasher()

def hash_password(password: str) -> str:
    return _ph.hash(password)          # úsalo en /signup

def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _ph.verify(password_hash, password)   # ojo: el hash va primero
    except (VerifyMismatchError, InvalidHashError):
        return False

#------ Session Tokens ------
SECRET_KEY = os.environ["ANCHOR_SECRET_KEY"]
ALGORITHM = "HS256"
TOKEN_TTL = timedelta(days=30)

def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "iat": now, "exp": now + TOKEN_TTL}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        return None

_bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> dict:
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = database.get_user_by_id(user_id)
    if user is None:
        # el token es válido pero el usuario fue borrado después de emitirlo
        raise HTTPException(status_code=401, detail="User no longer exists")

    return user