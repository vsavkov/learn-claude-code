export type HealthResponse = {
  status: 'ok' | 'degraded';
  gatewayReachable: boolean;
  gatewayStatusCode?: number;
  timestamp: string;
};

export type ToolCall = {
  id: string;
  name: string;
  input: Record<string, unknown>;
  status: 'success' | 'error';
  durationMs: number;
};

export type QueryResponse = {
  answer: string;
  toolCalls: ToolCall[];
  timingMs: number;
  requestId: string;
  timestamp: string;
  debug?: {
    rawGatewayPayload: unknown;
  };
};

export type ErrorResponse = {
  errorCode: string;
  message: string;
  requestId?: string;
  details?: unknown;
};
