import { HealthResponse } from '../lib/types';

type Props = {
  health: HealthResponse | null;
};

export function HealthBadge({ health }: Props) {
  const healthy = health?.status === 'ok';

  return (
    <div className={`badge ${healthy ? 'badge-ok' : 'badge-degraded'}`}>
      <span className="dot" />
      <span>{healthy ? 'Gateway Healthy' : 'Gateway Degraded'}</span>
    </div>
  );
}
