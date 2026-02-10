import { NextResponse } from 'next/server';
import { checkGatewayHealth } from '../../../lib/server/gatewayClient';

export async function GET() {
  const health = await checkGatewayHealth();

  return NextResponse.json({
    status: health.ok ? 'ok' : 'degraded',
    gatewayReachable: health.ok,
    gatewayStatusCode: health.statusCode,
    timestamp: new Date().toISOString()
  });
}
