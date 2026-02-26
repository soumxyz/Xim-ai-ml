interface ProbabilityGaugeProps {
  probability: number;
  status: "Approved" | "Rejected";
}

const ProbabilityGauge = ({ probability, status }: ProbabilityGaugeProps) => {
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (probability / 100) * circumference;
  const isApproved = status === "Approved";

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative w-32 h-32">
        <svg className="w-32 h-32 -rotate-90" viewBox="0 0 120 120">
          <circle
            cx="60"
            cy="60"
            r="54"
            fill="none"
            stroke="hsl(var(--border))"
            strokeWidth="8"
          />
          <circle
            cx="60"
            cy="60"
            r="54"
            fill="none"
            stroke={isApproved ? "hsl(var(--success))" : "hsl(var(--destructive))"}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold text-foreground">{probability}%</span>
          <span className="text-[10px] text-muted-foreground uppercase tracking-wider">Probability</span>
        </div>
      </div>
    </div>
  );
};

export default ProbabilityGauge;
