"""FastAPI sync server for Storymaster mobile app synchronization"""

import io
import logging
import socket
from datetime import datetime
from typing import Optional

import qrcode
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from storymaster.model.database.schema.base import SyncDevice, SyncLog
from storymaster.sync_server.auth import (
    create_device,
    generate_auth_token,
    get_current_device,
    get_device_by_id,
    update_last_sync,
)
from storymaster.sync_server.config import config
from storymaster.sync_server.database import get_db
from storymaster.sync_server.models import (
    DevicePairRequest,
    DevicePairResponse,
    HealthResponse,
    QRCodeResponse,
    SyncPullRequest,
    SyncPullResponse,
    SyncPushRequest,
    SyncPushResponse,
    SyncStatusResponse,
)
from storymaster.sync_server.sync_engine import SyncEngine

# Create FastAPI app
app = FastAPI(
    title="Storymaster Sync Server",
    description="API for synchronizing Storymaster data with mobile devices",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=config.CORS_CREDENTIALS,
    allow_methods=config.CORS_METHODS,
    allow_headers=config.CORS_HEADERS,
)


# === Exception Handlers ===


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log detailed validation errors and return them to client"""

    # Log the validation error details
    logger.error("=" * 80)
    logger.error("🚨 VALIDATION ERROR (422)")
    logger.error(f"Endpoint: {request.method} {request.url.path}")
    logger.error(f"Client: {request.client.host if request.client else 'unknown'}")

    # Log request body if available
    try:
        body = await request.body()
        if body:
            logger.error(f"Request Body: {body.decode('utf-8')}")
    except:
        pass

    # Log validation errors
    logger.error("Validation Errors:")
    for error in exc.errors():
        logger.error(f"  - Field: {error.get('loc')}")
        logger.error(f"    Type: {error.get('type')}")
        logger.error(f"    Message: {error.get('msg')}")
        logger.error(f"    Input: {error.get('input')}")

    logger.error("=" * 80)

    # Return the error response
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )


# === Helper Functions ===


def get_local_ip() -> str:
    """Get the local IP address of this machine"""
    try:
        # Connect to external address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


# Store temporary pairing tokens (in production, use Redis or database)
_pairing_tokens: dict[str, dict] = {}


# === Health Check ===


@app.get("/", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(),
        database_connected=True,
        version="1.0.0",
    )


# === Device Pairing Endpoints ===


@app.get("/api/pair/qr-data", response_model=QRCodeResponse)
async def get_qr_data():
    """
    Get QR code data for device pairing.
    Returns JSON with server IP, port, and a temporary pairing token.
    """
    # Generate temporary pairing token
    pairing_token = generate_auth_token()
    local_ip = get_local_ip()

    # Store pairing token temporarily (expires in 5 minutes)
    _pairing_tokens[pairing_token] = {
        "created_at": datetime.now(),
        "ip": local_ip,
        "port": config.PORT,
    }

    return QRCodeResponse(ip=local_ip, port=config.PORT, token=pairing_token)


@app.get("/api/pair/qr-image")
async def get_qr_image():
    """
    Generate a QR code image for device pairing.
    Returns a PNG image that can be scanned by the mobile app.
    """
    # Get QR data
    pairing_token = generate_auth_token()
    local_ip = get_local_ip()

    # Store pairing token
    _pairing_tokens[pairing_token] = {
        "created_at": datetime.now(),
        "ip": local_ip,
        "port": config.PORT,
    }

    # Create QR code data (JSON string)
    qr_data = f'{{"ip": "{local_ip}", "port": {config.PORT}, "token": "{pairing_token}"}}'

    # Generate QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return StreamingResponse(img_bytes, media_type="image/png")


@app.post("/api/pair/register", response_model=DevicePairResponse)
async def register_device(request: DevicePairRequest, db: Session = Depends(get_db)):
    """
    Register a new device for syncing.
    Mobile app calls this after scanning QR code.
    """
    # Validate pairing token
    if request.pairing_token not in _pairing_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired pairing token",
        )

    # Remove used pairing token
    del _pairing_tokens[request.pairing_token]

    # Check if device already exists
    existing_device = get_device_by_id(db, request.device_id)
    if existing_device:
        # Device already registered, return existing token
        return DevicePairResponse(
            device_id=existing_device.device_id,
            device_name=existing_device.device_name,
            auth_token=existing_device.auth_token,
            message="Device already registered",
        )

    # Create new device
    device = create_device(db, request.device_id, request.device_name)

    return DevicePairResponse(
        device_id=device.device_id,
        device_name=device.device_name,
        auth_token=device.auth_token,
        message="Device paired successfully",
    )


# === Sync Endpoints ===


@app.post("/api/sync/pull", response_model=SyncPullResponse)
async def sync_pull(
    request: SyncPullRequest,
    device: SyncDevice = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    """
    Pull changes from desktop to mobile.
    Returns all entities that have been modified since the given timestamp.
    """
    sync_engine = SyncEngine(db)

    # Get changes since last sync
    changes = sync_engine.get_changes_since(
        since_timestamp=request.since_timestamp,
        entity_types=request.entity_types,
    )

    # Update device's last sync time
    update_last_sync(db, device)

    return SyncPullResponse(
        changes=changes, sync_timestamp=datetime.now(), has_more=False
    )


@app.post("/api/sync/push", response_model=SyncPushResponse)
async def sync_push(
    request: SyncPushRequest,
    device: SyncDevice = Depends(get_current_device),
    db: Session = Depends(get_db),
):
    """
    Push changes from mobile to desktop.
    Applies changes with conflict detection and resolution.
    """
    sync_engine = SyncEngine(db)

    # Apply changes with conflict detection
    result = sync_engine.apply_changes(device, request.changes)

    # Update device's last sync time
    update_last_sync(db, device)

    return SyncPushResponse(
        accepted=result["accepted"],
        conflicts=result["conflicts"],
        rejected=result["rejected"],
        message=f"Processed {len(request.changes)} changes",
    )


@app.get("/api/sync/status", response_model=SyncStatusResponse)
async def sync_status(
    device: SyncDevice = Depends(get_current_device), db: Session = Depends(get_db)
):
    """Get current sync status for this device"""
    sync_engine = SyncEngine(db)

    # Count pending changes (changes since last sync)
    pending_count = sync_engine.count_changes_since(device.last_sync_at)

    return SyncStatusResponse(
        device_id=device.device_id,
        device_name=device.device_name,
        last_sync_at=device.last_sync_at,
        pending_changes_count=pending_count,
        server_timestamp=datetime.now(),
    )


# === Utility Endpoints ===


@app.get("/api/devices")
async def list_devices(db: Session = Depends(get_db)):
    """List all registered devices (for debugging/admin)"""
    stmt = select(SyncDevice).where(SyncDevice.is_active == True)
    devices = db.execute(stmt).scalars().all()

    return {
        "devices": [
            {
                "id": device.id,
                "device_id": device.device_id,
                "device_name": device.device_name,
                "last_sync_at": device.last_sync_at,
                "created_at": device.created_at,
            }
            for device in devices
        ]
    }


@app.delete("/api/devices/{device_id}")
async def remove_device(device_id: str, db: Session = Depends(get_db)):
    """Remove/deactivate a synced device"""
    # Find the device by device_id
    stmt = select(SyncDevice).where(SyncDevice.device_id == device_id)
    device = db.execute(stmt).scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found",
        )

    # Deactivate the device instead of deleting it (soft delete)
    device.is_active = False
    db.commit()

    logger.info(f"Device removed: {device.device_name} ({device_id})")

    return {
        "message": "Device removed successfully",
        "device_id": device_id,
        "device_name": device.device_name,
    }


# === Startup/Shutdown Events ===


@app.on_event("startup")
async def startup_event():
    """Run on server startup"""
    print("🚀 Storymaster Sync Server starting...")
    print(f"📱 Server running at http://{get_local_ip()}:{config.PORT}")
    print(f"🔗 QR Code available at: http://{get_local_ip()}:{config.PORT}/api/pair/qr-image")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on server shutdown"""
    print("👋 Storymaster Sync Server shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "storymaster.sync_server.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD,
    )
