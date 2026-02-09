import { ErrorResponse, HealthResponse, QueryResponse } from './types';

const baseUrl = process.env.NEXT_PUBLIC_BFF_BASE_URL ?? 'http://127.0.0.1:3001';

export const fetchHealth = async (): Promise<HealthResponse> => {
  const response = await fetch(`${baseUrl}/api/health`, {
    cache: 'no-store'
  });

  if (!response.ok) {
    throw new Error('BFF health endpoint failed');
  }

  return (await response.json()) as HealthResponse;
};

export const sendQuery = async (query: string): Promise<QueryResponse> => {
  const response = await fetch(`${baseUrl}/api/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ query })
  });

  const body = (await response.json().catch(() => ({}))) as QueryResponse | ErrorResponse;

  if (!response.ok) {
    const errorBody = body as ErrorResponse;
    throw new Error(`${errorBody.errorCode ?? 'request_failed'}: ${errorBody.message ?? 'Unknown error'}`);
  }

  return body as QueryResponse;
};
