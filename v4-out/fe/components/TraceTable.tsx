import { ToolCall } from '../lib/types';

type Props = {
  rows: ToolCall[];
};

export function TraceTable({ rows }: Props) {
  const displayRows = [...rows].reverse();

  return (
    <div className="panel">
      <h2>Tool Trace</h2>
      {rows.length === 0 ? (
        <p className="muted">No tool calls captured yet.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Tool</th>
              <th>Status</th>
              <th>Duration</th>
              <th>Input</th>
            </tr>
          </thead>
          <tbody>
            {displayRows.map((row) => (
              <tr key={row.id}>
                <td>{row.name}</td>
                <td>{row.status}</td>
                <td>{row.durationMs} ms</td>
                <td><code>{JSON.stringify(row.input)}</code></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
