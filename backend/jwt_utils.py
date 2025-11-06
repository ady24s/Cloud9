# backend/jwt_utils.py
import os
import time
import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv("SESSION_SECRET_KEY", "devsecret")
EXP_MIN = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # Default: 24h

def issue_access_token(user_id: int) -> str:
    now = int(time.time())
    payload = {"sub": str(user_id), "iat": now, "exp": now + EXP_MIN * 60}
    return jwt.encode(payload, SECRET, algorithm="HS256")

def verify_access_token(token: str) -> int:
    payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    return int(payload["sub"])
