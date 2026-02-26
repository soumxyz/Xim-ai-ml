import { StatusBadge } from './StatusBadge';
import { Clock } from 'lucide-react';

export function RecentChecksPanel({ checks }) {
  if (checks.length === 0) {
    return (
      <aside className="bg-card border border-border rounded-lg p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4">Recent Checks</h3>
        <p className="text-sm text-muted-foreground">
          No recent verification checks yet. Submit a title to get started.
        </p>
      </aside>
    );
  }

  return (
    <aside className="bg-card border border-border rounded-lg p-6">
      <h3 className="text-lg font-semibold text-foreground mb-4">Recent Checks</h3>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {checks.map((check) => (
          <div
            key={check.id}
            className="flex items-start justify-between gap-3 p-3 rounded border border-border hover:bg-muted transition-colors"
          >
            <div className="min-w-0 flex-1">
              <p className="font-medium text-foreground truncate text-sm">
                {check.title}
              </p>
              <div className="flex items-center gap-2 mt-1">
                <Clock className="w-3 h-3 text-muted-foreground flex-shrink-0" />
                <span className="text-xs text-muted-foreground">
                  {new Date(check.timestamp).toLocaleTimeString()}
                </span>
              </div>
            </div>

            <div className="flex flex-col items-end gap-1">
              <StatusBadge status={check.status} size="sm" />
              <span className="text-xs text-muted-foreground">
                {check.probability}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}
