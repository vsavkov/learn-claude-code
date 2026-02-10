'use client';

import { useEffect, useState } from 'react';
import { AnswerPanel } from '../components/AnswerPanel';
import { HealthBadge } from '../components/HealthBadge';
import { QueryForm } from '../components/QueryForm';
import { TraceTable } from '../components/TraceTable';
import { fetchHealth, sendQuery } from '../lib/api';
import { HealthResponse, QueryResponse } from '../lib/types';

export default function Page() {
  const [query, setQuery] = useState('show all running labs');
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadHealth = async () => {
      try {
        const status = await fetchHealth();
        setHealth(status);
      } catch {
        setHealth({
          status: 'degraded',
          gatewayReachable: false,
          timestamp: new Date().toISOString()
        });
      }
    };

    loadHealth();
    const interval = window.setInterval(loadHealth, 10000);
    return () => window.clearInterval(interval);
  }, []);

  const onSubmit = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await sendQuery(query);
      setResult(response);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Query failed';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page">
      <header className="hero">
        <h1>Containerlab Control Surface</h1>
        <p>Dashboard + chat console</p>
        <HealthBadge health={health} />
      </header>

      <section className="grid">
        <QueryForm value={query} onChange={setQuery} onSubmit={onSubmit} loading={loading} />
        <AnswerPanel
          answer={result?.answer ?? null}
          error={error}
          timingMs={result?.timingMs ?? null}
          requestId={result?.requestId ?? null}
        />
      </section>

      <section>
        <TraceTable rows={result?.toolCalls ?? []} />
      </section>
    </main>
  );
}
