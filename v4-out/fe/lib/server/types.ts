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
