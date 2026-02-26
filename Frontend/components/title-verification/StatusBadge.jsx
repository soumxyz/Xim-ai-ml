import { Check, X } from 'lucide-react';
import { cn } from '@/lib/utils';

export function StatusBadge({ status, size = 'md' }) {
  const isApproved = status === 'Approved';

  return (
    <div
      className={cn(
        'flex items-center gap-2 rounded-md px-3 py-2 font-semibold',
        isApproved
          ? 'bg-success/20 text-success border border-success/30'
          : 'bg-destructive/20 text-destructive border border-destructive/30',
        size === 'sm' && 'text-sm',
        size === 'md' && 'text-base',
        size === 'lg' && 'text-lg'
      )}
    >
      {isApproved ? (
        <Check className="w-4 h-4" />
      ) : (
        <X className="w-4 h-4" />
      )}
      {status}
    </div>
  );
}
