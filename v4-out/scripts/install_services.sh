#!/usr/bin/env bash
set -euo pipefail

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Error: required command '$1' not found" >&2
    exit 1
  fi
}

escape_sed() {
  printf '%s' "$1" | sed -e 's/[\/&]/\\&/g'
}

if [[ -z "${CONTAINERLAB_AGENT_BASE_DIR:-}" ]]; then
  echo "Error: CONTAINERLAB_AGENT_BASE_DIR is not set" >&2
  echo "Example: export CONTAINERLAB_AGENT_BASE_DIR=/path/to/containerlab-agent" >&2
  exit 1
fi

require_cmd systemctl
require_cmd sed

BASE_DIR="$(cd "$CONTAINERLAB_AGENT_BASE_DIR" && pwd -P)"
UVICORN_BIN="$BASE_DIR/.venv/bin/uvicorn"
NPM_BIN="$(command -v npm || true)"

if [[ -z "$NPM_BIN" ]]; then
  echo "Error: npm was not found in PATH" >&2
  exit 1
fi

required_paths=(
  "$BASE_DIR/api_gateway.py"
  "$BASE_DIR/containerlab_agent.py"
  "$BASE_DIR/.env"
  "$BASE_DIR/requirements.txt"
  "$BASE_DIR/.venv"
  "$BASE_DIR/fe"
  "$BASE_DIR/services/api-gateway.service.tpl"
  "$BASE_DIR/services/fe.service.tpl"
)

for path in "${required_paths[@]}"; do
  if [[ ! -e "$path" ]]; then
    echo "Error: required path not found: $path" >&2
    exit 1
  fi
done

if [[ ! -x "$UVICORN_BIN" ]]; then
  echo "Error: uvicorn executable not found at $UVICORN_BIN" >&2
  exit 1
fi

if ! systemctl --user show-environment >/dev/null 2>&1; then
  echo "Error: systemd user session is not available" >&2
  echo "Run this in a regular user login session with systemd --user enabled." >&2
  exit 1
fi

SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
mkdir -p "$SYSTEMD_USER_DIR"

echo "Building FE production bundle..."
(
  cd "$BASE_DIR/fe"
  "$NPM_BIN" run build
)

base_esc="$(escape_sed "$BASE_DIR")"
uvicorn_esc="$(escape_sed "$UVICORN_BIN")"
npm_esc="$(escape_sed "$NPM_BIN")"

render_unit() {
  local template="$1"
  local out="$2"

  sed \
    -e "s/__BASE_DIR__/$base_esc/g" \
    -e "s/__UVICORN_BIN__/$uvicorn_esc/g" \
    -e "s/__NPM_BIN__/$npm_esc/g" \
    "$template" > "$out"
}

render_unit "$BASE_DIR/services/api-gateway.service.tpl" "$SYSTEMD_USER_DIR/api-gateway.service"
render_unit "$BASE_DIR/services/fe.service.tpl" "$SYSTEMD_USER_DIR/fe.service"

echo "Reloading systemd user daemon..."
systemctl --user daemon-reload

echo "Enabling and starting api-gateway.service..."
systemctl --user enable --now api-gateway.service

echo "Enabling and starting fe.service..."
systemctl --user enable --now fe.service

cat <<INFO

Services installed and started.

Status:
  systemctl --user status api-gateway.service fe.service

Logs:
  journalctl --user -u api-gateway.service -f
  journalctl --user -u fe.service -f

Restart:
  systemctl --user restart api-gateway.service fe.service

Stop:
  systemctl --user stop api-gateway.service fe.service

Optional (persist user services after logout):
  loginctl enable-linger \$USER
INFO
