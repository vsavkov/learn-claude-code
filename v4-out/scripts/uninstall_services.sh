#!/usr/bin/env bash
set -euo pipefail

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Error: required command '$1' not found" >&2
    exit 1
  fi
}

require_cmd systemctl

SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICES=(api-gateway.service fe.service)

if ! systemctl --user show-environment >/dev/null 2>&1; then
  echo "Error: systemd user session is not available" >&2
  echo "Run this in a regular user login session with systemd --user enabled." >&2
  exit 1
fi

for service in "${SERVICES[@]}"; do
  if systemctl --user list-unit-files "$service" --no-legend 2>/dev/null | grep -q "$service"; then
    echo "Stopping $service (if running)..."
    systemctl --user stop "$service" || true

    echo "Disabling $service..."
    systemctl --user disable "$service" || true
  else
    echo "Service unit not registered: $service"
  fi
done

for service in "${SERVICES[@]}"; do
  unit_path="$SYSTEMD_USER_DIR/$service"
  if [[ -f "$unit_path" ]]; then
    echo "Removing $unit_path"
    rm -f "$unit_path"
  fi
done

echo "Reloading systemd user daemon..."
systemctl --user daemon-reload

echo "Resetting failed state (if any)..."
systemctl --user reset-failed || true

cat <<INFO

Services removed.

Verify:
  systemctl --user status api-gateway.service fe.service

Logs may still be available via journalctl history:
  journalctl --user -u api-gateway.service
  journalctl --user -u fe.service
INFO
