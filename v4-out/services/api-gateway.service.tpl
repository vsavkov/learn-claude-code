[Unit]
Description=Containerlab API Gateway
After=network.target

[Service]
Type=simple
WorkingDirectory=__BASE_DIR__
Environment=PYTHONUNBUFFERED=1
EnvironmentFile=__BASE_DIR__/.env
ExecStart=__UVICORN_BIN__ api_gateway:app --host 0.0.0.0 --port 9090
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
