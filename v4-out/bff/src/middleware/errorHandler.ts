import { NextFunction, Request, Response } from 'express';
import { HttpError } from '../services/gatewayClient.js';

export const errorHandler = (
  error: unknown,
  req: Request,
  res: Response,
  _next: NextFunction
): void => {
  if (error instanceof HttpError) {
    res.status(error.statusCode).json({
      errorCode: mapErrorCode(error.statusCode),
      message: error.message,
      requestId: res.getHeader('X-Request-ID'),
      details: error.details
    });
    return;
  }

  const message = error instanceof Error ? error.message : 'Unexpected server error';
  res.status(500).json({
    errorCode: 'internal_error',
    message,
    requestId: res.getHeader('X-Request-ID')
  });
};

const mapErrorCode = (statusCode: number): string => {
  switch (statusCode) {
    case 400:
      return 'bad_request';
    case 422:
      return 'validation_error';
    case 502:
      return 'gateway_upstream_error';
    case 504:
      return 'gateway_timeout';
    default:
      return 'gateway_error';
  }
};
