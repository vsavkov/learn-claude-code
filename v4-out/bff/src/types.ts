export type UiToolCall = {
  id: string;
  name: string;
  input: Record<string, unknown>;
  status: 'success' | 'error';
  durationMs: number;
};

export type UiQueryResponse = {
  answer: string;
  toolCalls: UiToolCall[];
  timingMs: number;
  requestId: string;
  timestamp: string;
  debug?: {
    rawGatewayPayload: unknown;
  };
};

export type UiErrorResponse = {
  errorCode: string;
  message: string;
  requestId?: string;
  details?: Record<string, unknown>;
};

export type GatewayQueryResponse = {
  answer: string;
  tool_calls: Array<{
    id: string;
    name: string;
    input: Record<string, unknown>;
    status: 'success' | 'error';
    duration_ms: number;
  }>;
  raw_outputs: Array<{
    tool_use_id: string;
    content: string;
  }>;
  timing_ms: number;
  model: string;
  request_id: string;
  timestamp: string;
};
