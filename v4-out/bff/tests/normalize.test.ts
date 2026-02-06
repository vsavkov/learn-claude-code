import { describe, expect, it } from 'vitest';
import { normalizeGatewayResponse } from '../src/mappers/normalize.js';

describe('normalizeGatewayResponse', () => {
  it('maps gateway payload fields to ui dto', () => {
    const result = normalizeGatewayResponse(
      {
        answer: 'hello',
        tool_calls: [
          {
            id: 't1',
            name: 'list_labs',
            input: { format: 'table' },
            status: 'success',
            duration_ms: 9
          }
        ],
        raw_outputs: [],
        timing_ms: 50,
        model: 'x',
        request_id: 'r1',
        timestamp: '2026-02-06T00:00:00Z'
      },
      false
    );

    expect(result.answer).toBe('hello');
    expect(result.toolCalls[0].durationMs).toBe(9);
    expect(result.requestId).toBe('r1');
    expect(result.debug).toBeUndefined();
  });
});
