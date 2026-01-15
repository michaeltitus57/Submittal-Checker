from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr

from app.auth import create_token, get_current_user_id
from app import users

app = FastAPI(title="Submittal Checker", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@app.post("/auth/signup")
def signup(body: SignupRequest):
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    try:
        user = users.create_user(body.email, body.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    token = create_token(user.id)
    return {"token": token}

@app.post("/auth/login")
def login(body: LoginRequest):
    user = users.authenticate(body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token(user.id)
    return {"token": token}

@app.get("/me")
def me(user_id: str = Depends(get_current_user_id)):
    user = users.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not fou
