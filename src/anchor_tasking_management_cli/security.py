# security.py
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
import os
from datetime import datetime, timedelta, timezone
import jwt

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