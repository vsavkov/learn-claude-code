const parsePort = (raw: string | undefined, fallback: number): number => {
  if (!raw) {
    return fallback;
  }
  const parsed = Number.parseInt(raw, 10);
  return Number.isFinite(parsed) ? parsed : fallback;
};

export const config = {
  port: parsePort(process.env.BFF_PORT, 3001),
  host: process.env.BFF_HOST ?? '127.0.0.1',
  gatewayBaseUrl: process.env.GATEWAY_BASE_URL ?? 'http://127.0.0.1:8080',
  requestTimeoutMs: parsePort(process.env.BFF_TIMEOUT_MS, 65000),
  debugMode: process.env.BFF_DEBUG === 'true',
  allowedOrigins: ['http://127.0.0.1:3000', 'http://localhost:3000']
};
