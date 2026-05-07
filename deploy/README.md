# Hosting the Storymaster sync server

These notes cover running the sync server on your own LAN host so multiple
desktops (and the mobile app) can share one canonical Storymaster database.

This setup assumes:
- **LAN-only** access (or via VPN). No TLS terminator is described here — add
  one if you ever expose the server beyond your network.
- **SQLite** as the backing database (same schema as the desktop app uses).
- **Single user** (the device-token auth model in the codebase has no concept
  of distinct human users).

## 1. Prepare the host

```bash
sudo useradd --system --create-home --home-dir /opt/storymaster storymaster
sudo mkdir -p /var/lib/storymaster
sudo chown storymaster:storymaster /var/lib/storymaster
```

Clone the repo (or unpack a release tarball) into `/opt/storymaster`, then
create a virtualenv and install requirements:

```bash
sudo -u storymaster bash -c '
  cd /opt/storymaster
  python -m venv .venv
  .venv/bin/pip install -r requirements.txt
'
```

## 2. Initialize the database

The sync server expects an existing schema. Two options:

**Fresh DB on the host:**

```bash
sudo -u storymaster STORYMASTER_DB_PATH=/var/lib/storymaster/storymaster.db \
    /opt/storymaster/.venv/bin/python /opt/storymaster/scripts/init_database.py
sudo -u storymaster STORYMASTER_DB_PATH=/var/lib/storymaster/storymaster.db \
    /opt/storymaster/.venv/bin/python /opt/storymaster/scripts/migrate_sync_uuid.py
```

**Seed from an existing desktop DB:** copy your local
`~/.local/share/storymaster/storymaster.db` to
`/var/lib/storymaster/storymaster.db`, then run the `migrate_sync_uuid.py` step
above to make sure every row has a `sync_uuid`.

## 3. Install the systemd unit

```bash
sudo cp deploy/storymaster-sync.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now storymaster-sync.service
sudo systemctl status storymaster-sync.service
```

The unit reads three env vars you may want to override (edit the unit file or
use `systemctl edit`):

| Env var | Purpose |
| --- | --- |
| `STORYMASTER_DB_PATH` | SQLite file the server reads/writes |
| `STORYMASTER_DB_URL` | Full SQLAlchemy URL — overrides `_DB_PATH` if set |
| `STORYMASTER_SYNC_HOST` | Bind address (default `0.0.0.0`) |
| `STORYMASTER_SYNC_PORT` | Bind port (default `8765`) |
| `SYNC_SECRET_KEY` | Reserved for future signing/rotation |

## 4. Pair a desktop

On the host, get a one-shot pairing token:

```bash
curl http://localhost:8765/api/pair/qr-data
# → {"ip": "...", "port": 8765, "token": "<one-shot-token>"}
```

In Storymaster on the desktop: **Tools → Configure Remote Sync...** Paste the
server URL (e.g. `http://10.0.0.5:8765`) and the token. Storymaster registers
this device, stores the resulting auth token at
`~/.config/storymaster/sync.json`, and from then on:

- Pulls on app startup
- Pushes on app shutdown
- Has a **Tools → Sync Now** entry for manual sync

## 5. Backups

The DB at `/var/lib/storymaster/storymaster.db` is the canonical store. A
nightly `sqlite3 storymaster.db ".backup /var/backups/storymaster-$(date +%F).db"`
or filesystem snapshot is enough. The desktops also retain their own local
copies, so a host loss isn't catastrophic — pair a fresh server, push from a
desktop, and you're recovered.

## 6. Common troubleshooting

- **`sqlite3.OperationalError: no such column: sync_uuid`** — the DB on the
  host hasn't been migrated. Run `scripts/migrate_sync_uuid.py` against it.
- **Pairing returns 401** — the token from `/api/pair/qr-data` expires after
  15 minutes. Get a fresh one.
- **Pushes report `rejected` rows** — usually means a referenced FK target
  (e.g. a Setting) hasn't replicated yet. Sync again, or pull first to
  populate parents.
- **Conflicts on the same row** — two desktops edited the same row between
  syncs. The server keeps the first push; the second is returned to the
  client as a conflict and isn't applied. Manual reconciliation needed.
