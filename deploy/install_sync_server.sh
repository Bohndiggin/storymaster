#!/usr/bin/env bash
# Install the Storymaster sync server on a Linux host.
#
# Usage (run as root, from inside the cloned repo):
#   sudo deploy/install_sync_server.sh
#
# Override defaults via env:
#   SYNC_USER=storymaster
#   INSTALL_DIR=/opt/storymaster
#   DATA_DIR=/var/lib/storymaster
#   PORT=8765
#   SEED_DB=/path/to/existing/storymaster.db   # optional: copy this DB instead of init'ing fresh
#   PYTHON_BIN=python3.11                       # path to a Python 3.11.x interpreter
#                                               # (e.g. ~/.pyenv/versions/3.11.9/bin/python)

set -euo pipefail

SYNC_USER="${SYNC_USER:-storymaster}"
INSTALL_DIR="${INSTALL_DIR:-/opt/storymaster}"
DATA_DIR="${DATA_DIR:-/var/lib/storymaster}"
PORT="${PORT:-8765}"
SERVICE_FILE="/etc/systemd/system/storymaster-sync.service"
SEED_DB="${SEED_DB:-}"
PYTHON_BIN="${PYTHON_BIN:-python3.11}"

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "ERROR: run this script as root (sudo)." >&2
  exit 1
fi

REPO_SRC="$(cd "$(dirname "$0")/.." && pwd)"
if [ ! -f "$REPO_SRC/requirements.txt" ]; then
  echo "ERROR: cannot find requirements.txt at $REPO_SRC. Run from inside the repo." >&2
  exit 1
fi
if [ ! -f "$REPO_SRC/deploy/storymaster-sync.service" ]; then
  echo "ERROR: cannot find deploy/storymaster-sync.service at $REPO_SRC." >&2
  exit 1
fi

# Resolve PYTHON_BIN to an absolute path the storymaster user can execute,
# even if it's a pyenv shim under the invoking user's $HOME.
if [ -x "$PYTHON_BIN" ]; then
  PYTHON_RESOLVED="$(readlink -f "$PYTHON_BIN")"
elif command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_RESOLVED="$(readlink -f "$(command -v "$PYTHON_BIN")")"
else
  echo "ERROR: PYTHON_BIN '$PYTHON_BIN' not found." >&2
  echo "Set PYTHON_BIN to a Python 3.11 interpreter, e.g.:" >&2
  echo "  PYTHON_BIN=\$(pyenv prefix 3.11.9)/bin/python sudo -E $0" >&2
  exit 1
fi

PY_VERSION="$("$PYTHON_RESOLVED" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if [ "$PY_VERSION" != "3.11" ]; then
  echo "ERROR: $PYTHON_RESOLVED is Python $PY_VERSION; this project requires 3.11." >&2
  exit 1
fi

# The system user we'll run the service as needs to be able to execute the
# Python interpreter and read its standard library. If $PYTHON_RESOLVED lives
# under someone's home dir (typical for pyenv), the system user usually can't
# even traverse the path. Detect this before we get cryptic errors later.
case "$PYTHON_RESOLVED" in
  /home/*|/root/*)
    cat >&2 <<EOF
ERROR: $PYTHON_RESOLVED lives under a personal home directory.
A system user (\"$SYNC_USER\") will not be able to traverse it, so the
sync service cannot run from there.

Two ways to fix this:

  1) Copy the pyenv install to a system path, then point PYTHON_BIN there:
       sudo cp -a "$(dirname "$(dirname "$PYTHON_RESOLVED")")" /opt/python-3.11
       sudo PYTHON_BIN=/opt/python-3.11/bin/python3.11 $0

  2) Install Python 3.11 system-wide via your distro and use that:
       e.g. \`pacman -S python311\` (Arch/CachyOS — check AUR if missing),
            \`apt install python3.11\` (Debian/Ubuntu),
            then re-run this script (default PYTHON_BIN=python3.11).
EOF
    exit 1
    ;;
esac

DB_PATH="$DATA_DIR/storymaster.db"

echo "==> Storymaster sync server install"
printf "    %-15s %s\n" "user:" "$SYNC_USER"
printf "    %-15s %s\n" "install dir:" "$INSTALL_DIR"
printf "    %-15s %s\n" "data dir:" "$DATA_DIR"
printf "    %-15s %s\n" "db path:" "$DB_PATH"
printf "    %-15s %s\n" "port:" "$PORT"
printf "    %-15s %s\n" "python:" "$PYTHON_RESOLVED ($PY_VERSION)"
printf "    %-15s %s\n" "source:" "$REPO_SRC"
[ -n "$SEED_DB" ] && printf "    %-15s %s\n" "seed db:" "$SEED_DB"
echo

# 1. System user
if id "$SYNC_USER" >/dev/null 2>&1; then
  echo "==> User $SYNC_USER already exists; skipping useradd."
else
  echo "==> Creating system user $SYNC_USER"
  useradd --system --create-home --home-dir "$INSTALL_DIR" --shell /usr/sbin/nologin "$SYNC_USER"
fi

# 2. Data dir
echo "==> Ensuring data dir $DATA_DIR"
mkdir -p "$DATA_DIR"
chown "$SYNC_USER:$SYNC_USER" "$DATA_DIR"
chmod 750 "$DATA_DIR"

# 3. Sync repo into INSTALL_DIR
echo "==> Syncing repo to $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete \
    --exclude=".venv" --exclude="__pycache__" --exclude=".git" \
    --exclude="*.pyc" --exclude=".pytest_cache" \
    "$REPO_SRC/" "$INSTALL_DIR/"
else
  # Fallback: cp preserves perms but doesn't prune stale files. Acceptable.
  cp -r "$REPO_SRC/." "$INSTALL_DIR/"
fi
chown -R "$SYNC_USER:$SYNC_USER" "$INSTALL_DIR"

# 4. Virtualenv + dependencies
echo "==> Setting up virtualenv with $PYTHON_RESOLVED and installing dependencies"
# If a venv already exists but was built with a different interpreter, recreate
# it to avoid silent version drift.
if [ -d "$INSTALL_DIR/.venv" ]; then
  EXISTING_VER="$("$INSTALL_DIR/.venv/bin/python" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "?")"
  if [ "$EXISTING_VER" != "3.11" ]; then
    echo "    existing venv is Python $EXISTING_VER; recreating with 3.11"
    rm -rf "$INSTALL_DIR/.venv"
  fi
fi
sudo -u "$SYNC_USER" bash -c "
  set -e
  cd '$INSTALL_DIR'
  if [ ! -d .venv ]; then '$PYTHON_RESOLVED' -m venv .venv; fi
  .venv/bin/pip install --upgrade pip --quiet
  .venv/bin/pip install -r requirements.txt --quiet
"

# 5. Database: seed, init, or migrate
if [ -n "$SEED_DB" ] && [ ! -f "$DB_PATH" ]; then
  echo "==> Seeding DB from $SEED_DB"
  cp "$SEED_DB" "$DB_PATH"
  chown "$SYNC_USER:$SYNC_USER" "$DB_PATH"
fi

if [ ! -f "$DB_PATH" ]; then
  echo "==> Initializing fresh database at $DB_PATH"
  sudo -u "$SYNC_USER" bash -c "
    cd '$INSTALL_DIR'
    PYTHONPATH='$INSTALL_DIR' STORYMASTER_DB_PATH='$DB_PATH' \
      .venv/bin/python scripts/init_database.py
  "
else
  echo "==> Database already present at $DB_PATH; skipping init."
fi

echo "==> Running sync_uuid migration (idempotent)"
sudo -u "$SYNC_USER" bash -c "
  cd '$INSTALL_DIR'
  PYTHONPATH='$INSTALL_DIR' STORYMASTER_DB_PATH='$DB_PATH' \
    .venv/bin/python scripts/migrate_sync_uuid.py
"

# 6. systemd unit (template + sed for the user-chosen paths)
echo "==> Installing systemd unit at $SERVICE_FILE"
TEMPLATE="$INSTALL_DIR/deploy/storymaster-sync.service"
# Escape forward slashes so sed handles paths safely.
esc_install="$(printf '%s' "$INSTALL_DIR" | sed 's|/|\\/|g')"
esc_data="$(printf '%s' "$DATA_DIR" | sed 's|/|\\/|g')"

sed \
  -e "s|/opt/storymaster|$INSTALL_DIR|g" \
  -e "s|/var/lib/storymaster|$DATA_DIR|g" \
  -e "s|^User=storymaster|User=$SYNC_USER|" \
  -e "s|^Group=storymaster|Group=$SYNC_USER|" \
  -e "s|STORYMASTER_SYNC_PORT=8765|STORYMASTER_SYNC_PORT=$PORT|" \
  "$TEMPLATE" > "$SERVICE_FILE"

systemctl daemon-reload
systemctl enable storymaster-sync.service >/dev/null
systemctl restart storymaster-sync.service

# 7. Confirm it's up
sleep 1
if systemctl is-active --quiet storymaster-sync.service; then
  echo "==> Service is running."
else
  echo "WARNING: service did not start cleanly. Inspect with:"
  echo "    journalctl -u storymaster-sync.service -n 50"
  exit 1
fi

# 8. Useful pointers
HOST_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
[ -z "$HOST_IP" ] && HOST_IP="localhost"
echo
echo "==> Done. Next steps:"
echo "    Server URL:   http://$HOST_IP:$PORT"
echo "    Get pairing token: curl http://localhost:$PORT/api/pair/qr-data"
echo "    Logs:         journalctl -u storymaster-sync.service -f"
echo "    Stop:         systemctl stop storymaster-sync.service"
echo
echo "    On a desktop: Tools → Configure Remote Sync... → paste URL + token."
