import { Check, X } from 'lucide-react';
import { cn } from '@/lib/utils';

export function AnalysisItem({
  label,
  value,
  isPercentage = false,
  isPassed,
}) {
  const displayPassed = isPassed ?? (typeof value === 'number' ? value >= 50 : value);
  const displayValue = isPercentage ? `${value}%` : typeof value === 'boolean' ? '' : String(value);

  return (
    <div className="flex items-center justify-between py-3 px-4 border-b border-border last:border-b-0">
      <span className="text-sm font-medium text-foreground">{label}</span>

      <div className="flex items-center gap-3">
        {displayValue && (
          <span className="text-sm font-semibold text-muted-foreground">{displayValue}</span>
        )}
        {typeof value === 'boolean' ? (
          value ? (
            <div className="flex items-center gap-1">
              <X className="w-4 h-4 text-destructive" />
              <span className="text-xs text-destructive">Violation</span>
            </div>
          ) : (
            <div className="flex items-center gap-1">
              <Check className="w-4 h-4 text-success" />
              <span className="text-xs text-success">Pass</span>
            </div>
          )
        ) : (
          displayPassed ? (
            <Check className="w-4 h-4 text-success" />
          ) : (
            <X className="w-4 h-4 text-destructive" />
          )
        )}
      </div>
    </div>
  );
}
