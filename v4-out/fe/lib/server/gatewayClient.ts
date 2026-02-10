import { ApiError } from './errors';
import { serverConfig } from './config';
import { GatewayQueryResponse } from './types';

type QueryArgs = {
  query: string;
  model?: string;
  maxTokens?: number;
  timeoutSeconds?: number;
};

export const queryGateway = async (args: QueryArgs): Promise<GatewayQueryResponse> => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), serverConfig.requestTimeoutMs);

  try {
    const response = await fetch(`${serverConfig.gatewayBaseUrl}/agent/query`, {
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
      throw new ApiError(
        response.status,
        mapErrorCode(response.status),
        (body.message as string | undefined) ?? 'Gateway request failed',
        body
      );
    }

    return body as unknown as GatewayQueryResponse;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiError(504, 'gateway_timeout', 'Gateway request timed out');
    }

    throw new ApiError(502, 'gateway_upstream_error', 'Could not connect to API gateway');
  } finally {
    clearTimeout(timeoutId);
  }
};

export const checkGatewayHealth = async (): Promise<{ ok: boolean; statusCode?: number }> => {
  try {
    const response = await fetch(`${serverConfig.gatewayBaseUrl}/health`, {
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

const mapErrorCode = (statusCode: number): string => {
  if (statusCode === 400 || statusCode === 422) {
    return 'validation_error';
  }
  if (statusCode === 504) {
    return 'gateway_timeout';
  }
  return 'gateway_upstream_error';
};
