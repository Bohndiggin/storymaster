# Storymaster Mobile Sync Implementation

## Overview

A complete FastAPI-based synchronization system has been implemented for bi-directional database sync between the Storymaster desktop app and mobile apps. The system includes QR code pairing, conflict detection, and automatic server lifecycle management.

## What Was Implemented

### 1. Database Schema Updates ✅

**File**: `storymaster/model/database/schema/base.py`

All database tables now include sync tracking fields:
- `created_at`: Timestamp when entity was created
- `updated_at`: Timestamp when entity was last modified (auto-updates)
- `deleted_at`: Timestamp for soft deletes (null if active)
- `version`: Integer counter for conflict detection

New tables added:
- `SyncDevice`: Stores registered mobile devices with auth tokens
- `SyncLog`: Audit log of all sync operations

### 2. Database Migration Script ✅

**File**: `scripts/migrate_sync_fields.py`

Automated migration script that:
- Backs up existing database before migration
- Adds sync fields to all existing tables
- Creates new sync-related tables
- Preserves all existing data
- Safe to run multiple times (idempotent)

**Usage**:
```bash
python scripts/migrate_sync_fields.py
```

### 3. FastAPI Sync Server ✅

**Directory**: `storymaster/sync_server/`

Complete sync server implementation with:

#### Core Modules:
- `main.py`: FastAPI application with all endpoints
- `config.py`: Server configuration (host, port, CORS, etc.)
- `auth.py`: Token-based authentication system
- `database.py`: SQLAlchemy session management
- `models.py`: Pydantic models for request/response validation
- `sync_engine.py`: Bi-directional sync logic with conflict detection
- `server_manager.py`: Server lifecycle management

#### API Endpoints:

**Health Check**:
- `GET /` - Server status and health check

**Device Pairing**:
- `GET /api/pair/qr-data` - Get QR code data as JSON
- `GET /api/pair/qr-image` - Get QR code as PNG image
- `POST /api/pair/register` - Register new device and get auth token

**Sync Operations** (authenticated):
- `POST /api/sync/pull` - Pull changes from desktop to mobile
- `POST /api/sync/push` - Push changes from mobile to desktop
- `GET /api/sync/status` - Get sync status and pending changes count

**Admin/Debug**:
- `GET /api/devices` - List all registered devices

### 4. Conflict Detection & Resolution ✅

**File**: `storymaster/sync_server/sync_engine.py`

Implemented version-based conflict detection:
- Compares `version` fields between desktop and mobile
- Detects when same entity was modified on both sides
- Returns detailed conflict information with both versions
- Supports three resolution strategies:
  - Desktop wins (for create conflicts)
  - Merge (for update conflicts)
  - Manual resolution (returned to mobile app)

### 5. Server Lifecycle Integration ✅

**File**: `storymaster/main.py`

Server automatically:
- Starts when desktop app launches
- Runs in background thread (non-blocking)
- Stops gracefully when app exits
- Auto-runs migration if needed

Integration added to `main()`:
```python
# Start sync server in background
sync_server_started = start_sync_server(host="0.0.0.0", port=8765)

# ... app runs ...

# Stop server on exit
stop_sync_server()
```

### 6. Comprehensive Test Suite ✅

**File**: `tests/test_sync_server.py`

Complete test coverage for:
- Health check endpoints
- QR code generation
- Device pairing (success, invalid token, duplicate device)
- Authentication (valid/invalid tokens, protected endpoints)
- Sync pull (empty, with data, incremental)
- Sync push (create, update, delete, conflicts)
- Sync status
- Conflict detection and resolution
- Device listing

**Run tests**:
```bash
pytest tests/test_sync_server.py -v
```

### 7. Dependencies ✅

**File**: `requirements.txt`

Added sync server dependencies:
- `fastapi==0.115.12` - Web framework
- `uvicorn[standard]==0.34.0` - ASGI server
- `pydantic==2.10.6` - Data validation
- `qrcode[pil]==8.1.1` - QR code generation
- `pillow==11.1.0` - Image processing
- `python-multipart==0.0.20` - Form data support

### 8. Documentation ✅

**File**: `storymaster/sync_server/README.md`

Complete documentation including:
- Quick start guide
- API endpoint reference
- Architecture overview
- Conflict resolution strategies
- Configuration options
- Troubleshooting guide
- Mobile integration examples (TypeScript)
- Security considerations

### 9. Standalone Server Script ✅

**File**: `start_sync_server.py`

Convenience script to run sync server independently:
```bash
python start_sync_server.py
```

Useful for:
- Testing without running full desktop app
- Development and debugging
- Running server on separate machine

## How to Use

### First-Time Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migration** (one-time):
   ```bash
   python scripts/migrate_sync_fields.py
   ```

3. **Start Storymaster**:
   ```bash
   python storymaster/main.py
   ```

You should see:
```
📱 Starting mobile sync server...
🚀 Sync server started at http://0.0.0.0:8765
✅ Sync server is running!
📲 Scan QR code at: http://localhost:8765/api/pair/qr-image
```

### Pairing Mobile Device

1. On your mobile device, open the sync settings
2. Tap "Scan QR Code"
3. Point camera at: `http://<your-computer-ip>:8765/api/pair/qr-image`
4. Device is paired! Auth token is stored securely

### Syncing Data

The mobile app will automatically:
1. **Pull changes** from desktop (incremental sync)
2. **Push local changes** to desktop
3. **Handle conflicts** if both sides modified same entity
4. **Track sync status** (last sync time, pending changes)

## Mobile App Integration

### Example TypeScript Code

**1. Pairing**:
```typescript
// Scan QR code
const qrData = JSON.parse(scannedCode);

// Register device
const response = await fetch(
  `http://${qrData.ip}:${qrData.port}/api/pair/register`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      device_id: DeviceInfo.getUniqueId(),
      device_name: DeviceInfo.getDeviceName(),
      pairing_token: qrData.token
    })
  }
);

const { auth_token } = await response.json();
// Store auth_token securely
```

**2. Pull Sync**:
```typescript
const response = await fetch(`${baseUrl}/api/sync/pull`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    since_timestamp: lastSyncTime,
    entity_types: null // All types
  })
});

const { changes } = await response.json();
// Apply changes to local database
```

**3. Push Sync**:
```typescript
const localChanges = await getLocalChanges();

const response = await fetch(`${baseUrl}/api/sync/push`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ changes: localChanges })
});

const { conflicts } = await response.json();
// Handle conflicts if any
```

## Architecture

### Sync Flow Diagram

```
┌──────────────┐                    ┌──────────────┐
│              │   QR Code Pair     │              │
│   Mobile     │◄──────────────────►│   Desktop    │
│     App      │                    │     App      │
│              │   Auth Token       │              │
└──────┬───────┘                    └──────┬───────┘
       │                                   │
       │  1. Pull Changes                  │
       │  POST /api/sync/pull             │
       ├──────────────────────────────────►│
       │                                   │
       │  2. Changes List                  │
       │  (with timestamps, versions)      │
       │◄──────────────────────────────────┤
       │                                   │
       │  3. Apply locally                 │
       │                                   │
       │  4. Push Changes                  │
       │  POST /api/sync/push             │
       ├──────────────────────────────────►│
       │                                   │
       │  5. Conflicts (if any)            │
       │◄──────────────────────────────────┤
       │                                   │
       │  6. Resolve conflicts             │
       │                                   │
       └───────────────────────────────────┘
```

### Database Schema

```
BaseTable (abstract)
├── created_at: DateTime
├── updated_at: DateTime
├── deleted_at: DateTime (nullable)
└── version: Integer

All entities inherit sync fields:
- User
- Storyline
- Setting
- Actor
- Location
- Faction
- ... (50+ tables)

New sync tables:
- SyncDevice (auth tokens)
- SyncLog (audit trail)
```

## Configuration

Edit `storymaster/sync_server/config.py`:

```python
HOST = "0.0.0.0"              # Listen on all interfaces
PORT = 8765                    # Server port
MAX_SYNC_BATCH_SIZE = 1000     # Max entities per sync
CONFLICT_RESOLUTION_MODE = "version"
```

## Security Notes

### Current Implementation (Development)
- ✅ Token-based authentication
- ✅ Secure token generation (32-byte random)
- ✅ HTTPS support ready (via reverse proxy)
- ⚠️ CORS allows all origins (for development)
- ⚠️ Server on all interfaces (0.0.0.0)

### For Production
1. Use HTTPS reverse proxy (nginx + SSL)
2. Restrict CORS to specific mobile app origin
3. Add firewall rules (only local network)
4. Implement token refresh mechanism
5. Add rate limiting

## Testing

**Run all tests**:
```bash
pytest tests/test_sync_server.py -v
```

**Test specific functionality**:
```bash
# Test pairing
pytest tests/test_sync_server.py::test_register_device_success -v

# Test sync pull
pytest tests/test_sync_server.py::test_sync_pull_with_data -v

# Test conflicts
pytest tests/test_sync_server.py::test_sync_push_conflict -v
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8765
lsof -i :8765

# Kill it or change PORT in config.py
```

### Migration Failed
```bash
# Check backup exists
ls ~/.local/share/storymaster/storymaster_backup_*.db

# Restore if needed
cp ~/.local/share/storymaster/storymaster_backup_*.db \
   ~/.local/share/storymaster/storymaster.db
```

### Mobile Can't Connect
1. Ensure both devices on same WiFi
2. Check firewall allows port 8765
3. Use actual IP (not localhost) in QR code
4. Verify server running: `curl http://localhost:8765/`

## Next Steps

### For Desktop App
- ✅ Server auto-starts (DONE)
- ✅ Migration runs automatically (DONE)
- 🔲 Add UI for viewing paired devices
- 🔲 Add UI for viewing sync status
- 🔲 Add button to show QR code on demand

### For Mobile App (Your Work)
- 🔲 Implement QR code scanner
- 🔲 Store auth token securely (Keychain/Keystore)
- 🔲 Implement sync service
- 🔲 Add conflict resolution UI
- 🔲 Schedule background sync
- 🔲 Show sync status in settings

## Files Created/Modified

### New Files
```
storymaster/sync_server/
├── __init__.py
├── main.py                    # FastAPI app
├── config.py                  # Configuration
├── auth.py                    # Authentication
├── database.py                # Session management
├── models.py                  # Pydantic models
├── sync_engine.py             # Sync logic
├── server_manager.py          # Lifecycle management
└── README.md                  # Documentation

scripts/
└── migrate_sync_fields.py     # Migration script

tests/
└── test_sync_server.py        # Test suite

Root:
├── start_sync_server.py       # Standalone server script
├── SYNC_IMPLEMENTATION.md     # This file
└── requirements.txt           # Updated with FastAPI deps
```

### Modified Files
```
storymaster/main.py
├── Added sync server imports
├── Added migration check
└── Added server start/stop in main()

storymaster/model/database/schema/base.py
├── Added DateTime import
├── Added sync fields to BaseTable
├── Added SyncDevice table
└── Added SyncLog table
```

## Summary

✅ **Complete bi-directional sync system implemented**
- QR code pairing for easy setup
- Version-based conflict detection
- Automatic server lifecycle management
- Comprehensive test coverage
- Full documentation

🎉 **Ready for mobile integration!**

The desktop side is complete. The mobile app just needs to:
1. Scan QR code
2. Call the REST API endpoints
3. Handle conflicts if any

All the heavy lifting (conflict detection, version tracking, data merging) is handled by the desktop server.
