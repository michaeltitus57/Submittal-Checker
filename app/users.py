import uuid
from dataclasses import dataclass
from typing import Dict, Optional

from app.auth import hash_password, verify_password

@dataclass
class User:
    id: str
    email: str
    password_hash: str

# In-memory store (resets on redeploy). OK for MVP testing.
_USERS_BY_EMAIL: Dict[str, User] = {}

def create_user(email: str, password: str) -> User:
    email = email.strip().lower()
    if email in _USERS_BY_EMAIL:
        raise ValueError("Email already registered")
    user = User(
        id=str(uuid.uuid4()),
        email=email,
        password_hash=hash_password(password),
    )
    _USERS_BY_EMAIL[email] = user
    return user

def authenticate(email: str, password: str) -> Optional[User]:
    email = email.strip().lower()
    user = _USERS_BY_EMAIL.get(email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def get_user_by_id(user_id: str) -> Optional[User]:
    for u in _USERS_BY_EMAIL.values():
        if u.id == user_id:
            return u
    return None
