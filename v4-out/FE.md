# FE App (Single Origin)

## Purpose

`fe/` is a single Next.js application that:
- serves the Web UI
- translates requests/responses between Web UI and backend
- avoids browser CORS by using same-origin `/api/*` routes

## Architecture

- Browser -> `fe` (UI + `/api/query`, `/api/health`)
- `fe` server routes -> FastAPI gateway (`api_gateway.py`)

## Environment

- `GATEWAY_BASE_URL` default: `http://127.0.0.1:8080`
- `FE_REQUEST_TIMEOUT_MS` default: `65000`
- `FE_DEBUG=true` includes raw gateway payload in `/api/query` response

## Run

Start backend gateway:

```bash
uvicorn api_gateway:app --host 127.0.0.1 --port 8080
```

Start FE:

```bash
cd fe
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:3000
```

## API

Health:

```bash
curl -s http://127.0.0.1:3000/api/health
```

Query:

```bash
curl -s http://127.0.0.1:3000/api/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"show all running labs"}'
```
