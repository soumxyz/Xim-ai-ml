const ProbabilityGauge = ({ probability, status }) => {
    const circumference = 2 * Math.PI * 54;
    const offset = circumference - (probability / 100) * circumference;
    
    const getColor = (prob, status) => {
        if (status === "Manual Review") return "#EAB308"; // Yellow-500
        if (prob >= 80) return "#10B981"; // Success Green
        if (prob <= 33) return "rgb(239, 68, 68)"; // Red
        if (prob <= 66) return "rgb(234, 179, 8)"; // Yellow
        return "rgb(34, 197, 94)"; // Green (default for >66 and <80)
    };

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
                        stroke={getColor(probability)}
                        strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray={circumference}
                        strokeDashoffset={offset}
                        className="transition-all duration-1000 ease-out"
                    />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-2xl font-bold text-foreground">{parseFloat(probability).toFixed(2)}%</span>
                    <span className="text-[10px] text-muted-foreground uppercase tracking-wider">Probability</span>
                </div>
            </div>
        </div>
    );
};

export default ProbabilityGauge;
