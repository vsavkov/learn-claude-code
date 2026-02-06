import { GatewayQueryResponse, UiQueryResponse } from '../types.js';

export const normalizeGatewayResponse = (
  payload: GatewayQueryResponse,
  debugMode: boolean
): UiQueryResponse => {
  const base: UiQueryResponse = {
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
    return base;
  }

  return {
    ...base,
    debug: {
      rawGatewayPayload: payload
    }
  };
};
