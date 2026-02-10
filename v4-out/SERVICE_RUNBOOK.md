# Service Runbook

## Services

- `api-gateway.service`
  - Binds `0.0.0.0:9090`
  - Runs `api_gateway.py` through project venv `uvicorn`

- `fe.service`
  - Binds `0.0.0.0:8080`
  - Runs Next.js FE in production mode
  - Uses `GATEWAY_BASE_URL=http://127.0.0.1:9090`

## Install and Start

```bash
export CONTAINERLAB_AGENT_BASE_DIR=/path/to/base
bash "$CONTAINERLAB_AGENT_BASE_DIR/scripts/install_services.sh"
```

## Health Checks

```bash
curl -s http://127.0.0.1:9090/health
curl -s http://127.0.0.1:8080/api/health
```

Query through FE API:

```bash
curl -s http://127.0.0.1:8080/api/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"show all running labs"}'
```

## Service Operations

```bash
systemctl --user status api-gateway.service fe.service
systemctl --user restart api-gateway.service fe.service
systemctl --user stop api-gateway.service fe.service
journalctl --user -u api-gateway.service -f
journalctl --user -u fe.service -f
```

## Uninstall Services

```bash
export CONTAINERLAB_AGENT_BASE_DIR=/path/to/base
bash "$CONTAINERLAB_AGENT_BASE_DIR/scripts/uninstall_services.sh"
```

## Notes

- Installer validates required paths under `CONTAINERLAB_AGENT_BASE_DIR`.
- Installer rebuilds FE (`npm run build`) before enabling services.
- If user services should survive logout:

```bash
loginctl enable-linger "$USER"
```
