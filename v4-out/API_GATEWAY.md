# Containerlab API Gateway

## Overview

`api_gateway.py` exposes a synchronous HTTP API on top of the containerlab agent functionality.

## Run

```bash
pip install -r requirements.txt
uvicorn api_gateway:app --host 127.0.0.1 --port 8080
```

## Endpoints

### `GET /health`

Response:

```json
{"status":"ok"}
```

### `POST /agent/query`

Request:

```json
{
  "query": "show all running labs",
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 4096,
  "timeout_seconds": 60
}
```

Response:

```json
{
  "answer": "I found 1 running lab...",
  "tool_calls": [
    {
      "id": "toolu_...",
      "name": "list_labs",
      "input": {"format": "table"},
      "status": "success",
      "duration_ms": 98
    }
  ],
  "raw_outputs": [
    {
      "tool_use_id": "toolu_...",
      "content": "<raw tool output>"
    }
  ],
  "timing_ms": 1530,
  "model": "claude-sonnet-4-5-20250929",
  "request_id": "uuid",
  "timestamp": "2026-02-06T00:00:00Z"
}
```

## Curl Tests

Run these commands after starting the server on `127.0.0.1:8080`.

Health check:

```bash
curl -s http://127.0.0.1:8080/health
```

Basic query:

```bash
curl -s http://127.0.0.1:8080/agent/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"show all running labs"}'
```

Query with explicit model and timeout:

```bash
curl -s http://127.0.0.1:8080/agent/query \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "show network interfaces",
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 2048,
    "timeout_seconds": 45
  }'
```

Validation error example (empty query, should return `422`):

```bash
curl -i http://127.0.0.1:8080/agent/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"   "}'
```

Config error example (missing `ANTHROPIC_API_KEY`, should return `500`):

```bash
env -u ANTHROPIC_API_KEY \
  uvicorn api_gateway:app --host 127.0.0.1 --port 8081

curl -i http://127.0.0.1:8081/agent/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"show all running labs"}'
```

## Notes

- Gateway is designed for localhost-only access in v1.
- `ANTHROPIC_API_KEY` must be set (or available in `.env`).
- Tool execution behavior is reused from `containerlab_agent.py` via `process_tool_call`.
