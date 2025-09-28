import os
import time
import jwt
from dotenv import load_dotenv

load_dotenv()

# ✅ Make sure this matches your .env
SECRET = os.getenv("SESSION_SECRET_KEY", "devsecret")
ALGORITHM = "HS256"
EXP_MIN = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # default 24 hours

def issue_access_token(user_id: int) -> str:
    now = int(time.time())
    payload = {"sub": str(user_id), "iat": now, "exp": now + EXP_MIN * 60}
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except jwt.ExpiredSignatureError:
        return None  # expired token
    except jwt.InvalidTokenError:
        return None  # invalid token
