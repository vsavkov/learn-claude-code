import cors from 'cors';
import express from 'express';
import { config } from './config.js';
import { errorHandler } from './middleware/errorHandler.js';
import { requestIdMiddleware } from './middleware/requestId.js';
import { healthRouter } from './routes/health.js';
import { queryRouter } from './routes/query.js';

export const app = express();

app.use(express.json({ limit: '1mb' }));
app.use(requestIdMiddleware);
app.use(
  cors({
    origin: (origin, callback) => {
      if (!origin || config.allowedOrigins.includes(origin)) {
        callback(null, true);
        return;
      }

      callback(new Error('CORS policy blocked this origin'));
    }
  })
);

app.use('/api/health', healthRouter);
app.use('/api/query', queryRouter);

app.use(errorHandler);

if (process.env.NODE_ENV !== 'test') {
  app.listen(config.port, config.host, () => {
    console.log(`BFF listening at http://${config.host}:${config.port}`);
  });
}
