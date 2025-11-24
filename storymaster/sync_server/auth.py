"""Authentication and authorization for the sync server"""

import secrets
import uuid
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session

from storymaster.model.database.schema.base import SyncDevice, SyncPairingToken
from storymaster.sync_server.database import get_db

# Security scheme
security = HTTPBearer()


def generate_auth_token() -> str:
    """Generate a secure random auth token"""
    return secrets.token_urlsafe(32)


def generate_device_id() -> str:
    """Generate a unique device ID"""
    return str(uuid.uuid4())


async def get_current_device(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> SyncDevice:
    """
    Validate auth token and return the authenticated device.
    Used as a FastAPI dependency for protected endpoints.
    """
    token = credentials.credentials

    # Query for device with this token
    stmt = select(SyncDevice).where(
        SyncDevice.auth_token == token, SyncDevice.is_active == True
    )
    device = db.execute(stmt).scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return device


def create_device(db: Session, device_id: str, device_name: str) -> SyncDevice:
    """Create a new sync device with auth token"""
    auth_token = generate_auth_token()

    device = SyncDevice(
        device_id=device_id, device_name=device_name, auth_token=auth_token, is_active=True
    )

    db.add(device)
    db.commit()
    db.refresh(device)

    return device


def get_device_by_id(db: Session, device_id: str) -> Optional[SyncDevice]:
    """Get device by device_id"""
    stmt = select(SyncDevice).where(SyncDevice.device_id == device_id)
    return db.execute(stmt).scalar_one_or_none()


def update_last_sync(db: Session, device: SyncDevice) -> None:
    """Update the last_sync_at timestamp for a device"""
    device.last_sync_at = datetime.now()
    db.commit()

def create_pairing_token(db: Session, expires_in_minutes: int = 15) -> SyncPairingToken:
    """Create and store a new pairing token in the database"""
    from datetime import timedelta, timezone

    token = generate_auth_token()
    # Use UTC timezone-aware datetime for consistency
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)

    pairing_token = SyncPairingToken(token=token, expires_at=expires_at)
    db.add(pairing_token)
    db.commit()
    db.refresh(pairing_token)
    return pairing_token


def consume_pairing_token(db: Session, token: str) -> bool:
    """
    Validate and consume a pairing token.
    Returns True if the token is valid and consumed, False otherwise.
    """
    from datetime import timezone

    # Use UTC timezone-aware datetime for consistency
    now = datetime.now(timezone.utc)

    stmt = select(SyncPairingToken).where(
        SyncPairingToken.token == token,
        SyncPairingToken.expires_at > now,
    )
    pairing_token = db.execute(stmt).scalar_one_or_none()

    if pairing_token:
        db.delete(pairing_token)
        db.commit()
        return True

    return False

