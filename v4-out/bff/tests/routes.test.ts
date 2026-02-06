import request from 'supertest';
import { afterEach, describe, expect, it, vi } from 'vitest';

vi.mock('../src/services/gatewayClient.js', () => {
  return {
    queryGateway: vi.fn(),
    healthGateway: vi.fn(),
    HttpError: class HttpError extends Error {
      statusCode: number;
      details?: Record<string, unknown>;

      constructor(message: string, statusCode: number, details?: Record<string, unknown>) {
        super(message);
        this.statusCode = statusCode;
        this.details = details;
      }
    }
  };
});

import { app } from '../src/server.js';
import { healthGateway, queryGateway } from '../src/services/gatewayClient.js';

afterEach(() => {
  vi.clearAllMocks();
});

describe('BFF routes', () => {
  it('returns health payload', async () => {
    vi.mocked(healthGateway).mockResolvedValue({ ok: true, statusCode: 200 });

    const response = await request(app).get('/api/health');

    expect(response.status).toBe(200);
    expect(response.body.status).toBe('ok');
    expect(response.body.gatewayReachable).toBe(true);
  });

  it('returns normalized query payload', async () => {
    vi.mocked(queryGateway).mockResolvedValue({
      answer: 'hello',
      tool_calls: [
        {
          id: 'a',
          name: 'list_labs',
          input: { format: 'table' },
          status: 'success',
          duration_ms: 10
        }
      ],
      raw_outputs: [],
      timing_ms: 123,
      model: 'm',
      request_id: 'rid',
      timestamp: '2026-02-06T00:00:00Z'
    });

    const response = await request(app).post('/api/query').send({ query: 'show labs' });

    expect(response.status).toBe(200);
    expect(response.body.answer).toBe('hello');
    expect(response.body.toolCalls[0].durationMs).toBe(10);
  });

  it('rejects empty query payload', async () => {
    const response = await request(app).post('/api/query').send({ query: '  ' });

    expect(response.status).toBe(400);
    expect(response.body.errorCode).toBe('bad_request');
  });
});
