import { randomUUID } from 'node:crypto';
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { queryGateway } from '../../../lib/server/gatewayClient';
import { normalizeGatewayResponse } from '../../../lib/server/normalize';
import { serverConfig } from '../../../lib/server/config';
import { ApiError } from '../../../lib/server/errors';

const querySchema = z.object({
  query: z.string().trim().min(1),
  model: z.string().optional(),
  maxTokens: z.number().int().positive().optional(),
  timeoutSeconds: z.number().int().min(1).max(120).optional()
});

export async function POST(request: NextRequest) {
  const requestId = randomUUID();

  try {
    const json = await request.json();
    const parsed = querySchema.safeParse(json);

    if (!parsed.success) {
      return NextResponse.json(
        {
          errorCode: 'bad_request',
          message: 'Invalid query payload',
          requestId,
          details: parsed.error.flatten()
        },
        { status: 400 }
      );
    }

    const gatewayResponse = await queryGateway(parsed.data);
    const response = normalizeGatewayResponse(gatewayResponse, serverConfig.debugMode);

    return NextResponse.json(response, {
      status: 200,
      headers: {
        'X-Request-ID': requestId
      }
    });
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json(
        {
          errorCode: error.errorCode,
          message: error.message,
          requestId,
          details: error.details
        },
        { status: error.statusCode }
      );
    }

    return NextResponse.json(
      {
        errorCode: 'internal_error',
        message: error instanceof Error ? error.message : 'Unexpected server error',
        requestId
      },
      { status: 500 }
    );
  }
}
