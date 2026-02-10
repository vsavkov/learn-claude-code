import { useEffect, useRef, useState } from 'react';

type Props = {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  loading: boolean;
};

export function QueryForm({ value, onChange, onSubmit, loading }: Props) {
  const [isExamplesOpen, setIsExamplesOpen] = useState(false);
  const examplesRef = useRef<HTMLDivElement | null>(null);
  const examples = [
    'show all running labs',
    'inspect interfaces for all nodes',
    'show topology and highlight issues',
    'generate mermaid diagram',
    'check if any interfaces are down',
    'summarize lab health and next steps'
  ];

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (!examplesRef.current) {
        return;
      }
      if (!examplesRef.current.contains(event.target as Node)) {
        setIsExamplesOpen(false);
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsExamplesOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, []);

  const onSelectExample = (example: string) => {
    onChange(example);
    setIsExamplesOpen(false);
  };

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
      <div className="query-actions">
        <button className="button" disabled={loading || value.trim().length === 0} onClick={onSubmit}>
          {loading ? 'Running...' : 'Run Query'}
        </button>

        <div className="examples" ref={examplesRef}>
          <button
            className="examples-toggle"
            type="button"
            aria-expanded={isExamplesOpen}
            onClick={() => setIsExamplesOpen((open) => !open)}
          >
            Query examples
          </button>

          {isExamplesOpen ? (
            <div className="examples-menu" role="listbox" aria-label="Query examples">
              {examples.map((example) => (
                <button
                  key={example}
                  className="examples-item"
                  type="button"
                  onClick={() => onSelectExample(example)}
                >
                  {example}
                </button>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
