import { Router } from 'express';
import { healthGateway } from '../services/gatewayClient.js';

export const healthRouter = Router();

healthRouter.get('/', async (_req, res) => {
  const status = await healthGateway();

  res.status(200).json({
    status: status.ok ? 'ok' : 'degraded',
    gatewayReachable: status.ok,
    gatewayStatusCode: status.statusCode,
    timestamp: new Date().toISOString()
  });
});
