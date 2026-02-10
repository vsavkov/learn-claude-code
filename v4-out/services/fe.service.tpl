[Unit]
Description=Containerlab FE (Next.js)
After=network.target api-gateway.service
Requires=api-gateway.service

[Service]
Type=simple
WorkingDirectory=__BASE_DIR__/fe
Environment=NODE_ENV=production
Environment=GATEWAY_BASE_URL=http://127.0.0.1:9090
ExecStart=__NPM_BIN__ run start -- --hostname 0.0.0.0 --port 8080
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
