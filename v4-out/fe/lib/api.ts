import { ErrorResponse, HealthResponse, QueryResponse } from './types';

export const fetchHealth = async (): Promise<HealthResponse> => {
  const response = await fetch('/api/health', {
    cache: 'no-store'
  });

  if (!response.ok) {
    throw new Error('FE health endpoint failed');
  }

  return (await response.json()) as HealthResponse;
};

export const sendQuery = async (query: string): Promise<QueryResponse> => {
  const response = await fetch('/api/query', {
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
