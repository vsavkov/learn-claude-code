# Next.js Web UI + BFF

## Architecture

- `ui/` is a Next.js frontend.
- `bff/` is a dedicated Express server that calls the FastAPI gateway.
- Browser never calls FastAPI directly.

Flow:

1. Web UI -> `POST /api/query` on BFF.
2. BFF -> `POST /agent/query` on FastAPI gateway.
3. BFF normalizes response and returns DTO to UI.

## Environment

Gateway:

- `ANTHROPIC_API_KEY` must be set.

BFF:

- `GATEWAY_BASE_URL` (default `http://127.0.0.1:8080`)
- `BFF_HOST` (default `127.0.0.1`)
- `BFF_PORT` (default `3001`)
- `BFF_TIMEOUT_MS` (default `65000`)
- `BFF_DEBUG=true` to include raw gateway payload in UI response.

UI:

- `NEXT_PUBLIC_BFF_BASE_URL` (default `http://127.0.0.1:3001`)

## Run Locally

Start gateway (root):

```bash
uvicorn api_gateway:app --host 127.0.0.1 --port 8080
```

Start BFF:

```bash
cd bff
npm install
npm run dev
```

Start UI:

```bash
cd ui
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:3000
```

## BFF API

### `GET /api/health`

```bash
curl -s http://127.0.0.1:3001/api/health
```

### `POST /api/query`

```bash
curl -s http://127.0.0.1:3001/api/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"show all running labs"}'
```

## UI Features (v1)

- Dashboard health badge (polling every 10s)
- Query console
- Answer panel with request metadata
- Tool trace table

## Tests

BFF tests:

```bash
cd bff
npm test
```
