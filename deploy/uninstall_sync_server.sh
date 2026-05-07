#!/usr/bin/env bash
# Uninstall the Storymaster sync server.
#
# Usage (run as root):
#   sudo deploy/uninstall_sync_server.sh
#
# By default this removes the systemd unit and the install dir but PRESERVES
# the database and the system user. To go further, opt in via env:
#   REMOVE_DATA=1                     also delete $DATA_DIR (the canonical DB!)
#   REMOVE_USER=1                     also delete the system user
#   PYTHON_COPY_DIR=/opt/python-3.11  also rm -rf that path (e.g. the pyenv copy)
#   FORCE=1                           skip confirmation prompts
#
# Other env overrides match the install script:
#   SYNC_USER=storymaster
#   INSTALL_DIR=/opt/storymaster
#   DATA_DIR=/var/lib/storymaster

set -euo pipefail

SYNC_USER="${SYNC_USER:-storymaster}"
INSTALL_DIR="${INSTALL_DIR:-/opt/storymaster}"
DATA_DIR="${DATA_DIR:-/var/lib/storymaster}"
SERVICE_FILE="/etc/systemd/system/storymaster-sync.service"
SERVICE_NAME="storymaster-sync.service"
PYTHON_COPY_DIR="${PYTHON_COPY_DIR:-}"
REMOVE_DATA="${REMOVE_DATA:-0}"
REMOVE_USER="${REMOVE_USER:-0}"
FORCE="${FORCE:-0}"

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "ERROR: run this script as root (sudo)." >&2
  exit 1
fi

confirm() {
  if [ "$FORCE" = "1" ]; then
    return 0
  fi
  local prompt="$1"
  read -r -p "$prompt [y/N] " ans
  case "$ans" in
    y|Y|yes|YES) return 0 ;;
    *) return 1 ;;
  esac
}

# Summary
echo "==> Storymaster sync server uninstall"
printf "    %-15s %s\n" "user:"            "$SYNC_USER"
printf "    %-15s %s\n" "install dir:"     "$INSTALL_DIR (will be removed)"
printf "    %-15s %s\n" "data dir:"        "$DATA_DIR ($([ "$REMOVE_DATA" = 1 ] && echo "WILL BE REMOVED" || echo "kept"))"
printf "    %-15s %s\n" "service:"         "$SERVICE_NAME (will be stopped + removed)"
[ "$REMOVE_USER" = 1 ] && printf "    %-15s %s\n" "system user:" "$SYNC_USER (WILL BE DELETED)"
[ -n "$PYTHON_COPY_DIR" ] && printf "    %-15s %s\n" "python copy:" "$PYTHON_COPY_DIR (will be removed)"
echo

if ! confirm "Proceed with uninstall?"; then
  echo "Cancelled."
  exit 0
fi

# 1. Stop + disable systemd service
if systemctl list-unit-files "$SERVICE_NAME" 2>/dev/null | grep -q "^$SERVICE_NAME"; then
  echo "==> Stopping and disabling $SERVICE_NAME"
  systemctl stop "$SERVICE_NAME" 2>/dev/null || true
  systemctl disable "$SERVICE_NAME" 2>/dev/null || true
else
  echo "==> Service $SERVICE_NAME not registered; skipping stop."
fi

if [ -f "$SERVICE_FILE" ]; then
  echo "==> Removing $SERVICE_FILE"
  rm -f "$SERVICE_FILE"
  systemctl daemon-reload
  systemctl reset-failed "$SERVICE_NAME" 2>/dev/null || true
fi

# 2. Install dir
if [ -d "$INSTALL_DIR" ]; then
  echo "==> Removing $INSTALL_DIR"
  rm -rf "$INSTALL_DIR"
else
  echo "==> $INSTALL_DIR doesn't exist; nothing to remove."
fi

# 3. Optional: data dir
if [ "$REMOVE_DATA" = "1" ]; then
  if [ -d "$DATA_DIR" ]; then
    if confirm "REMOVE_DATA=1 set — really delete $DATA_DIR (canonical sync DB)?"; then
      echo "==> Removing $DATA_DIR"
      rm -rf "$DATA_DIR"
    else
      echo "==> Skipping data dir removal."
    fi
  else
    echo "==> $DATA_DIR doesn't exist; nothing to remove."
  fi
else
  if [ -d "$DATA_DIR" ]; then
    echo "==> Keeping data at $DATA_DIR (set REMOVE_DATA=1 to delete)"
  fi
fi

# 4. Optional: system user
if [ "$REMOVE_USER" = "1" ]; then
  if id "$SYNC_USER" >/dev/null 2>&1; then
    echo "==> Deleting system user $SYNC_USER"
    userdel "$SYNC_USER" 2>/dev/null || \
      echo "    userdel returned non-zero (user may have running processes); inspect manually."
  else
    echo "==> User $SYNC_USER doesn't exist."
  fi
fi

# 5. Optional: copied python install
if [ -n "$PYTHON_COPY_DIR" ]; then
  if [ -d "$PYTHON_COPY_DIR" ]; then
    if confirm "Really delete $PYTHON_COPY_DIR?"; then
      echo "==> Removing $PYTHON_COPY_DIR"
      rm -rf "$PYTHON_COPY_DIR"
    else
      echo "==> Skipping python copy removal."
    fi
  else
    echo "==> $PYTHON_COPY_DIR doesn't exist."
  fi
fi

echo
echo "==> Uninstall complete."
[ "$REMOVE_DATA" != "1" ] && [ -d "$DATA_DIR" ] && \
  echo "    Note: $DATA_DIR was preserved. Delete manually or re-run with REMOVE_DATA=1."
