type Props = {
  answer: string | null;
  error: string | null;
  timingMs: number | null;
  requestId: string | null;
};

export function AnswerPanel({ answer, error, timingMs, requestId }: Props) {
  return (
    <div className="panel">
      <h2>Result</h2>
      {error ? <p className="error">{error}</p> : null}
      {!error && !answer ? <p className="muted">No query executed yet.</p> : null}
      {answer ? <pre className="answer">{answer}</pre> : null}
      {timingMs !== null ? <p className="meta">Gateway roundtrip: {timingMs} ms</p> : null}
      {requestId ? <p className="meta">Request ID: {requestId}</p> : null}
    </div>
  );
}
