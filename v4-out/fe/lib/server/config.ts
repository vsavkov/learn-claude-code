const parseIntOr = (raw: string | undefined, fallback: number): number => {
  if (!raw) {
    return fallback;
  }

  const parsed = Number.parseInt(raw, 10);
  return Number.isFinite(parsed) ? parsed : fallback;
};

export const serverConfig = {
  gatewayBaseUrl: process.env.GATEWAY_BASE_URL ?? 'http://127.0.0.1:8080',
  requestTimeoutMs: parseIntOr(process.env.FE_REQUEST_TIMEOUT_MS, 65000),
  debugMode: process.env.FE_DEBUG === 'true'
};
