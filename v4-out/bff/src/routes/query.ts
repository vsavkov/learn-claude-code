import { Router } from 'express';
import { z } from 'zod';
import { config } from '../config.js';
import { normalizeGatewayResponse } from '../mappers/normalize.js';
import { queryGateway } from '../services/gatewayClient.js';

const querySchema = z.object({
  query: z.string().trim().min(1),
  model: z.string().optional(),
  maxTokens: z.number().int().positive().optional(),
  timeoutSeconds: z.number().int().min(1).max(120).optional()
});

export const queryRouter = Router();

queryRouter.post('/', async (req, res, next) => {
  try {
    const parsed = querySchema.safeParse(req.body);

    if (!parsed.success) {
      res.status(400).json({
        errorCode: 'bad_request',
        message: 'Invalid query payload',
        requestId: res.getHeader('X-Request-ID'),
        details: parsed.error.flatten()
      });
      return;
    }

    const gatewayResponse = await queryGateway(parsed.data);
    const normalized = normalizeGatewayResponse(gatewayResponse, config.debugMode);

    res.status(200).json(normalized);
  } catch (error) {
    next(error);
  }
});
