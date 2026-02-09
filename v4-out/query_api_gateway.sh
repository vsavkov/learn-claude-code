#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 \"your query\""
  exit 1
fi

QUERY="$*"
GATEWAY_URL="${GATEWAY_URL:-http://127.0.0.1:8080}"

curl -s "${GATEWAY_URL}/agent/query" \
  -H 'Content-Type: application/json' \
  -d "{\"query\":\"${QUERY//\"/\\\"}\"}"

echo
