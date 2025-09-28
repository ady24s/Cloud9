# backend/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from dotenv import load_dotenv
import httpx
import os
import json
import urllib.parse

from backend.database import SessionLocal
from backend.models import User, CloudCredential
from backend.jwt_utils import issue_access_token, verify_access_token
from backend.crypto_utils import encrypt_text

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")

# ===========================================================
#  GOOGLE & MICROSOFT LOGIN
# ===========================================================
config = Config(environ={
    "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", ""),
    "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", ""),
    "MICROSOFT_CLIENT_ID": os.getenv("MICROSOFT_CLIENT_ID", ""),
    "MICROSOFT_CLIENT_SECRET": os.getenv("MICROSOFT_CLIENT_SECRET", ""),
})
oauth = OAuth(config)

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

login_tenant = os.getenv("MICROSOFT_TENANT_ID", "common")
oauth.register(
    name="microsoft",
    client_id=os.getenv("MICROSOFT_CLIENT_ID", ""),
    client_secret=os.getenv("MICROSOFT_CLIENT_SECRET", ""),
    server_metadata_url=f"https://login.microsoftonline.com/{login_tenant}/v2.0/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo") or {}
    email = userinfo.get("email")
    sub = userinfo.get("sub")
    if not email:
        raise HTTPException(status_code=400, detail="Google login failed: no email returned")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, provider="google", provider_id=sub)
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = issue_access_token(user.id)
    return RedirectResponse(f"{FRONTEND_BASE_URL}/auth/callback?token={urllib.parse.quote(access_token)}")

@router.get("/microsoft/login")
async def microsoft_login(request: Request):
    redirect_uri = request.url_for("microsoft_callback")
    return await oauth.microsoft.authorize_redirect(request, redirect_uri)

@router.get("/microsoft/callback")
async def microsoft_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.microsoft.authorize_access_token(request)
    claims = token.get("userinfo") or token.get("id_token_claims") or {}
    email = claims.get("email") or claims.get("preferred_username")
    sub = claims.get("sub") or claims.get("oid")
    if not email:
        raise HTTPException(status_code=400, detail="Microsoft login failed: no email returned")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, provider="microsoft", provider_id=sub)
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = issue_access_token(user.id)
    return RedirectResponse(f"{FRONTEND_BASE_URL}/auth/callback?token={urllib.parse.quote(access_token)}")


# ===========================================================
#  AZURE (ARM CONNECT)
# ===========================================================
AZURE_CLIENT_ID = os.getenv("AZURE_APP_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_APP_CLIENT_SECRET")
AZURE_REDIRECT_URI = os.getenv("AZURE_OAUTH_REDIRECT_URI", "http://localhost:8000/auth/azure/callback")
AZURE_TENANT = os.getenv("AZURE_TENANT_ID", "common")
AZURE_SCOPE = os.getenv("AZURE_MANAGEMENT_SCOPE", "https://management.azure.com//.default offline_access")

AZURE_AUTH_URL = f"https://login.microsoftonline.com/{AZURE_TENANT}/oauth2/v2.0/authorize"
AZURE_TOKEN_URL = f"https://login.microsoftonline.com/{AZURE_TENANT}/oauth2/v2.0/token"

def _ensure_azure_env():
    missing = []
    if not AZURE_CLIENT_ID: missing.append("AZURE_APP_CLIENT_ID")
    if not AZURE_CLIENT_SECRET: missing.append("AZURE_APP_CLIENT_SECRET")
    if not AZURE_REDIRECT_URI: missing.append("AZURE_OAUTH_REDIRECT_URI")
    if missing:
        raise HTTPException(500, f"Azure OAuth not configured. Missing: {', '.join(missing)}")

@router.get("/azure/login")
async def azure_login(token: str = Query(...)):
    _ensure_azure_env()
    user = verify_access_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token. Please log in again.")

    state_data = json.dumps({"token": token})
    query_params = {
        "client_id": AZURE_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": AZURE_REDIRECT_URI,
        "response_mode": "query",
        "scope": AZURE_SCOPE,
        "state": urllib.parse.quote(state_data),
    }
    url = f"{AZURE_AUTH_URL}?{urllib.parse.urlencode(query_params)}"
    return RedirectResponse(url)

@router.get("/azure/callback")
async def azure_callback(code: str, state: str, db: Session = Depends(get_db)):
    _ensure_azure_env()
    try:
        state_data = json.loads(urllib.parse.unquote(state))
        token = state_data.get("token")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    user = verify_access_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")

    token_data = {
        "client_id": AZURE_CLIENT_ID,
        "client_secret": AZURE_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": AZURE_REDIRECT_URI,
    }

    async with httpx.AsyncClient(timeout=25) as client:
        token_resp =_
