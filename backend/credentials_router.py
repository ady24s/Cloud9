from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import SessionLocal
from backend.models import CloudCredential
from backend.schemas import CloudCredentialIn, CloudCredentialOut
from backend.crypto_utils import encrypt_text
from backend.auth_deps import get_current_user

router = APIRouter(prefix="/credentials", tags=["credentials"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=CloudCredentialOut, status_code=status.HTTP_201_CREATED)
def upsert_credentials(
    payload: CloudCredentialIn,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
):
    if payload.provider not in {"aws", "azure", "gcp"}:
        raise HTTPException(status_code=400, detail="provider must be aws|azure|gcp")

    cred = (
        db.query(CloudCredential)
        .filter(CloudCredential.user_id == user.id, CloudCredential.provider == payload.provider)
        .first()
    )
    if not cred:
        cred = CloudCredential(provider=payload.provider, user_id=user.id)
        db.add(cred)

    cred.access_key_enc = encrypt_text(payload.access_key)
    cred.secret_key_enc = encrypt_text(payload.secret_key)
    cred.extra_json_enc = encrypt_text(payload.extra_json)

    db.commit()
    db.refresh(cred)
    return cred


@router.get("", response_model=List[CloudCredentialOut])
def list_credentials(db: Session = Depends(get_db), user = Depends(get_current_user)):
    creds = db.query(CloudCredential).filter(CloudCredential.user_id == user.id).all()
    return creds


@router.get("/{provider}", response_model=CloudCredentialOut)
def get_provider_credentials(provider: str, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if provider not in {"aws", "azure", "gcp"}:
        raise HTTPException(status_code=400, detail="provider must be aws|azure|gcp")

    cred = (
        db.query(CloudCredential)
        .filter(CloudCredential.user_id == user.id, CloudCredential.provider == provider)
        .first()
    )
    if not cred:
        raise HTTPException(status_code=404, detail="credentials not found")
    return cred


@router.delete("/{provider}", status_code=status.HTTP_204_NO_CONTENT)
def delete_provider_credentials(provider: str, db: Session = Depends(get_db), user = Depends(get_current_user)):
    cred = (
        db.query(CloudCredential)
        .filter(CloudCredential.user_id == user.id, CloudCredential.provider == provider)
        .first()
    )
    if not cred:
        raise HTTPException(status_code=404, detail="credentials not found")
    db.delete(cred)
    db.commit()
    return None
