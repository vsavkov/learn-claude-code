import { config } from '../config.js';
import { GatewayQueryResponse } from '../types.js';

export class HttpError extends Error {
  statusCode: number;
  details?: Record<string, unknown>;

  constructor(message: string, statusCode: number, details?: Record<string, unknown>) {
    super(message);
    this.statusCode = statusCode;
    this.details = details;
  }
}

type QueryArgs = {
  query: string;
  model?: string;
  maxTokens?: number;
  timeoutSeconds?: number;
};

export const queryGateway = async (args: QueryArgs): Promise<GatewayQueryResponse> => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), config.requestTimeoutMs);

  try {
    const response = await fetch(`${config.gatewayBaseUrl}/agent/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      signal: controller.signal,
      body: JSON.stringify({
        query: args.query,
        model: args.model,
        max_tokens: args.maxTokens,
        timeout_seconds: args.timeoutSeconds
      })
    });

    const body = (await response.json().catch(() => ({}))) as Record<string, unknown>;

    if (!response.ok) {
      throw new HttpError(
        (body.message as string | undefined) ?? 'Gateway request failed',
        response.status,
        body as Record<string, unknown>
      );
    }

    return body as unknown as GatewayQueryResponse;
  } catch (error) {
    if (error instanceof HttpError) {
      throw error;
    }

    if (error instanceof Error && error.name === 'AbortError') {
      throw new HttpError('Gateway request timed out', 504);
    }

    throw new HttpError('Could not connect to API gateway', 502);
  } finally {
    clearTimeout(timeoutId);
  }
};

export const healthGateway = async (): Promise<{ ok: boolean; statusCode?: number }> => {
  try {
    const response = await fetch(`${config.gatewayBaseUrl}/health`, {
      method: 'GET'
    });

    return {
      ok: response.ok,
      statusCode: response.status
    };
  } catch {
    return {
      ok: false
    };
  }
};
