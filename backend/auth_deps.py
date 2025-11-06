# backend/auth_deps.py
from fastapi import Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.jwt_utils import verify_access_token
from backend.models import User

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_id(request: Request, authorization: str = Header(None)) -> int:
    token = None

    # 1. Prefer Authorization header
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]

    # 2. Fallback: look for token in query param
    if not token:
        token = request.query_params.get("token")

    if not token:
        raise HTTPException(status_code=401, detail="Authorization token missing")

    try:
        return verify_access_token(token)
    except Exception:
        raise HTTPException(401, "Invalid or expired token")

def get_current_user(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)) -> User:
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(401, "User not found")
    return user
