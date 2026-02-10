import { describe, expect, it } from 'vitest';
import { normalizeGatewayResponse } from '../lib/server/normalize';

describe('normalizeGatewayResponse', () => {
  it('maps gateway payload to FE DTO', () => {
    const payload = {
      answer: 'ok',
      tool_calls: [
        {
          id: 't1',
          name: 'list_labs',
          input: { format: 'table' },
          status: 'success' as const,
          duration_ms: 12
        }
      ],
      raw_outputs: [],
      timing_ms: 200,
      model: 'm',
      request_id: 'r1',
      timestamp: '2026-02-09T00:00:00Z'
    };

    const result = normalizeGatewayResponse(payload, false);
    expect(result.answer).toBe('ok');
    expect(result.toolCalls[0].durationMs).toBe(12);
    expect(result.requestId).toBe('r1');
    expect(result.debug).toBeUndefined();
  });
});
