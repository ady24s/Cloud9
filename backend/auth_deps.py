from fastapi import Depends, HTTPException, Header
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

def get_current_user_id(authorization: str = Header(None)) -> int:
    """
    Extract user_id from Authorization Bearer token.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authorization: Bearer <token> required")

    token = authorization.split(" ", 1)[1]
    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
    return user_id

def get_current_user(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> User:
    """
    Return user object from database.
    """
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found or deleted")
    return user
