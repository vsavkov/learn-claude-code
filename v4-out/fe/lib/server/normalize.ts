import { QueryResponse } from '../types';
import { GatewayQueryResponse } from './types';

export const normalizeGatewayResponse = (
  payload: GatewayQueryResponse,
  debugMode: boolean
): QueryResponse => {
  const normalized: QueryResponse = {
    answer: payload.answer,
    toolCalls: payload.tool_calls.map((call) => ({
      id: call.id,
      name: call.name,
      input: call.input,
      status: call.status,
      durationMs: call.duration_ms
    })),
    timingMs: payload.timing_ms,
    requestId: payload.request_id,
    timestamp: payload.timestamp
  };

  if (!debugMode) {
    return normalized;
  }

  return {
    ...normalized,
    debug: {
      rawGatewayPayload: payload
    }
  };
};
