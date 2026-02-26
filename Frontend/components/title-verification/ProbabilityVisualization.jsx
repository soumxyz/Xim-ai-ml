import { cn } from '@/lib/utils';

export function ProbabilityVisualization({
  probability,
  status,
}) {
  const isApproved = status === 'Approved';

  return (
    <div className="flex flex-col items-center gap-6">
      <div className="relative w-32 h-32 rounded-full border-8 flex items-center justify-center" 
           style={{
             borderColor: isApproved ? '#2D5016' : '#5A2C2C',
             background: `conic-gradient(${isApproved ? '#2D5016' : '#5A2C2C'} 0deg ${probability * 3.6}deg, #E0E0E0 ${probability * 3.6}deg 360deg)`
           }}>
        <div className="w-28 h-28 rounded-full bg-background flex items-center justify-center">
          <div className="text-center">
            <div className="text-3xl font-bold text-foreground">{probability}%</div>
            <div className="text-xs text-muted-foreground">Verification</div>
          </div>
        </div>
      </div>

      <div className="text-center">
        <p className="text-sm font-medium text-muted-foreground mb-1">
          {isApproved ? 'Approval' : 'Rejection'} Probability
        </p>
        <p className={cn(
          'text-sm font-semibold',
          isApproved ? 'text-success' : 'text-destructive'
        )}>
          {isApproved ? 'High confidence approval' : 'High confidence rejection'}
        </p>
      </div>
    </div>
  );
}
