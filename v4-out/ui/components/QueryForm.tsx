type Props = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  loading: boolean;
};

export function QueryForm({ value, onChange, onSubmit, loading }: Props) {
  return (
    <div className="panel">
      <label htmlFor="query" className="label">Query</label>
      <textarea
        id="query"
        className="textarea"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Ask about your labs, interfaces, topology, or health"
        rows={5}
      />
      <button className="button" disabled={loading || value.trim().length === 0} onClick={onSubmit}>
        {loading ? 'Running...' : 'Run Query'}
      </button>
    </div>
  );
}
