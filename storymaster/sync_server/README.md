# Storymaster Sync Server

FastAPI-based synchronization server for bi-directional sync between Storymaster desktop and mobile apps.

## Features

- **QR Code Pairing**: Easy device registration via QR code scanning
- **Bi-directional Sync**: Full two-way synchronization between desktop and mobile
- **Conflict Detection**: Version-based conflict detection with merge support
- **Timestamp Tracking**: All entities track `created_at`, `updated_at`, `deleted_at`, and `version`
- **Soft Deletes**: Entities are marked as deleted rather than hard-deleted
- **RESTful API**: Clean REST API for sync operations
- **Authentication**: Token-based authentication for secure device access

## Quick Start

### 1. Install Dependencies

The sync server dependencies are already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Run Database Migration

Add timestamp tracking fields to your existing database:

```bash
python scripts/migrate_sync_fields.py
```

This adds `created_at`, `updated_at`, `deleted_at`, and `version` fields to all tables, plus creates `sync_device` and `sync_log` tables.

### 3. Start the Application

The sync server starts automatically when you launch Storymaster:

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

### 4. Pair Mobile Device

On your mobile app:
1. Navigate to Settings → Sync
2. Tap "Scan QR Code"
3. Scan the QR code from: `http://<your-ip>:8765/api/pair/qr-image`
4. Device is now paired and can sync!

## API Endpoints

### Health Check

```
GET /
```

Returns server status and version.

### Device Pairing

#### Get QR Code Data (JSON)

```
GET /api/pair/qr-data
```

Returns JSON with IP, port, and temporary pairing token.

#### Get QR Code Image

```
GET /api/pair/qr-image
```

Returns PNG image of QR code for scanning.

#### Register Device

```
POST /api/pair/register
Content-Type: application/json

{
  "device_id": "uuid-from-mobile",
  "device_name": "My iPhone",
  "pairing_token": "token-from-qr-code"
}
```

Returns permanent `auth_token` for API access.

### Sync Operations (Authenticated)

All sync endpoints require Bearer token authentication:

```
Authorization: Bearer <auth_token>
```

#### Pull Changes from Desktop

```
POST /api/sync/pull
Content-Type: application/json

{
  "since_timestamp": "2024-01-01T00:00:00Z",  // null for full sync
  "entity_types": ["actor", "location"]        // null for all types
}
```

Returns list of changes since timestamp.

#### Push Changes to Desktop

```
POST /api/sync/push
Content-Type: application/json

{
  "changes": [
    {
      "entity_type": "actor",
      "entity_id": 123,
      "operation": "update",  // "create", "update", or "delete"
      "data": { ... },
      "version": 2,
      "updated_at": "2024-01-15T12:00:00Z"
    }
  ]
}
```

Returns accepted count and any conflicts.

#### Get Sync Status

```
GET /api/sync/status
```

Returns device info, last sync time, and pending changes count.

### Admin/Debug

#### List Devices

```
GET /api/devices
```

Returns all registered devices (for debugging).

## Architecture

### Components

- **main.py**: FastAPI application with all endpoints
- **config.py**: Server configuration settings
- **auth.py**: Authentication and token management
- **database.py**: SQLAlchemy session management
- **models.py**: Pydantic models for API validation
- **sync_engine.py**: Core sync logic and conflict resolution
- **server_manager.py**: Server lifecycle management (start/stop)

### Database Schema

All entities now include:

- `created_at`: Timestamp when entity was created
- `updated_at`: Timestamp when entity was last modified
- `deleted_at`: Timestamp when entity was soft-deleted (null if active)
- `version`: Integer version counter for conflict detection

New tables:

- `sync_device`: Registered mobile devices
- `sync_log`: Audit log of sync operations

### Conflict Resolution

**Version-Based Conflicts**: When mobile and desktop have different versions of the same entity:

1. **Check Version**: Compare `version` field and `updated_at` timestamp
2. **Detect Conflict**: If versions don't match, conflict occurred
3. **Resolution Strategies**:
   - **Desktop Wins**: Desktop version takes precedence (default for create conflicts)
   - **Merge**: Attempt to merge both versions (default for update conflicts)
   - **Manual**: Return conflict to mobile app for user resolution

**Conflict Response**:

```json
{
  "accepted": 5,
  "rejected": 0,
  "conflicts": [
    {
      "entity_type": "actor",
      "entity_id": 123,
      "mobile_version": 2,
      "desktop_version": 3,
      "mobile_data": { ... },
      "desktop_data": { ... },
      "resolution": "merge"
    }
  ]
}
```

### Sync Flow

#### Initial Sync (Mobile First Launch)

1. Mobile scans QR code and registers
2. Mobile calls `/api/sync/pull` with `since_timestamp: null`
3. Desktop returns all entities (full sync)
4. Mobile stores all entities locally

#### Incremental Sync

1. Mobile calls `/api/sync/pull` with last sync timestamp
2. Desktop returns only entities modified after timestamp
3. Mobile applies changes locally

4. Mobile calls `/api/sync/push` with local changes
5. Desktop applies changes with conflict detection
6. Mobile handles any conflicts returned

## Configuration

Edit `storymaster/sync_server/config.py`:

```python
class SyncServerConfig:
    HOST = "0.0.0.0"              # Listen on all interfaces
    PORT = 8765                    # Server port
    MAX_SYNC_BATCH_SIZE = 1000     # Max entities per sync
    CONFLICT_RESOLUTION_MODE = "version"  # "version" or "timestamp"
```

## Testing

Run the test suite:

```bash
pytest tests/test_sync_server.py -v
```

Tests cover:
- Device pairing
- Authentication
- Sync pull/push operations
- Conflict detection
- Incremental sync

## Security Considerations

### For Development

- Server listens on `0.0.0.0` (all interfaces) for local network access
- CORS allows all origins (`*`)
- Pairing tokens expire after use (stored in memory)

### For Production

1. **HTTPS**: Use reverse proxy (nginx) with SSL certificates
2. **Firewall**: Restrict port 8765 to local network only
3. **CORS**: Specify exact mobile app origin
4. **Token Expiry**: Implement token refresh mechanism
5. **Rate Limiting**: Add rate limiting to prevent abuse

## Troubleshooting

### Server Won't Start

**Port Already in Use**:
```bash
# Find process using port 8765
lsof -i :8765

# Kill process or change port in config.py
```

**Database Migration Failed**:
```bash
# Manually run migration
python scripts/migrate_sync_fields.py

# Check for backup
ls ~/.local/share/storymaster/storymaster_backup_*.db
```

### Mobile Can't Connect

1. **Check Network**: Ensure mobile and desktop on same network
2. **Check Firewall**: Desktop firewall may block port 8765
3. **Check IP**: Use actual IP (not `localhost`) in QR code
4. **Check Server Status**: Look for "Sync server is running!" message

### Sync Conflicts

**Too Many Conflicts**:
- Sync more frequently to avoid divergence
- Implement conflict resolution UI on mobile
- Use timestamp comparison for tie-breaking

**Data Not Syncing**:
- Check auth token validity (`/api/sync/status`)
- Verify entity types are included in sync request
- Check server logs for errors

## Mobile App Integration

### Pairing Flow (TypeScript)

```typescript
// 1. Scan QR code to get connection data
const qrData = JSON.parse(scannedQRCode); // {ip, port, token}

// 2. Register device
const response = await fetch(`http://${qrData.ip}:${qrData.port}/api/pair/register`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    device_id: DeviceInfo.getUniqueId(),
    device_name: DeviceInfo.getDeviceName(),
    pairing_token: qrData.token
  })
});

const { auth_token } = await response.json();
// Store auth_token securely (AsyncStorage/Keychain)
```

### Sync Flow (TypeScript)

```typescript
// Pull changes from desktop
const pullResponse = await fetch(`${baseUrl}/api/sync/pull`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    since_timestamp: lastSyncTimestamp,
    entity_types: null // All types
  })
});

const { changes } = await pullResponse.json();

// Apply changes to local database
for (const change of changes) {
  await applyChange(change);
}

// Push local changes
const localChanges = await getLocalChanges(lastSyncTimestamp);
const pushResponse = await fetch(`${baseUrl}/api/sync/push`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ changes: localChanges })
});

const { conflicts } = await pushResponse.json();

// Handle conflicts
if (conflicts.length > 0) {
  await handleConflicts(conflicts);
}
```

## Future Enhancements

- [ ] Real-time sync with WebSockets
- [ ] Selective entity sync (user chooses what to sync)
- [ ] Multi-device sync with last-write-wins
- [ ] Sync progress indicators
- [ ] Background sync on mobile
- [ ] Sync analytics and monitoring
- [ ] Cloud relay for remote sync (not just local network)

## Support

For issues or questions:
- Check the main Storymaster CLAUDE.md documentation
- Review FastAPI docs: https://fastapi.tiangolo.com/
- File issues on GitHub: https://github.com/anthropics/storymaster/issues
