# app/crypto_utils.py
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    raise RuntimeError("FERNET_KEY is missing in .env")
fernet = Fernet(FERNET_KEY.encode() if not FERNET_KEY.startswith("gAAAA") else FERNET_KEY)

def encrypt_text(plain: str | None) -> str | None:
    if plain is None:
        return None
    return fernet.encrypt(plain.encode()).decode()

def decrypt_text(token: str | None) -> str | None:
    if token is None:
        return None
    return fernet.decrypt(token.encode()).decode()
