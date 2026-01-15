from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from passlib.hash import bcrypt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Change this later to an env var (we'll do that next)
JWT_SECRET = "CHANGE_ME_TO_A_LONG_RANDOM_STRING"
JWT_ALG = "HS256"
TOKEN_DAYS = 7

bearer = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.verify(password, password_hash)

def create_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=TOKEN_DAYS)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def get_current_user_id(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer),
) -> str:
    if creds is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    return decode_token(creds.credentials)
