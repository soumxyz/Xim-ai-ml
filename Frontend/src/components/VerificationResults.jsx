import { Card, CardContent } from "@/components/ui/card";
import ProbabilityGauge from "./ProbabilityGauge";

const VerificationResults = ({ result }) => {
    const isApproved = result.status === "Approved";
    const suggestions = result.suggestions;

    return (
        <Card className="border-border bg-card shadow-sm">
            <CardContent className="p-6 md:p-8">
                <div className="flex flex-col md:flex-row gap-8 items-center md:items-start">
                    {/* Left: Info */}
                    <div className="flex-1 space-y-5 w-full">
                        <div className="flex flex-wrap items-center gap-3">
                            <h2 className="text-lg font-semibold text-foreground">Verification Result:</h2>
                            <span className={`text-lg font-semibold ${isApproved ? "text-green-600 dark:text-green-400" :
                                    result.status === "Rejected" ? "text-red-600 dark:text-red-400" :
                                        "text-yellow-600 dark:text-yellow-400"
                                }`}>
                                {result.status}
                            </span>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <InfoRow label="Submitted Title" value={result.submitted_title} />
                            <InfoRow label="Closest Match" value={result.closest_match} />
                            <InfoRow label="Similarity Score" value={`${result.similarity_score}%`} />
                            <InfoRow
                                label="Verification Probability"
                                value={`${parseFloat(result.verification_probability).toFixed(2)}%`}
                                bold
                            />
                        </div>

                        {/* Suggestions Section */}
                        {suggestions && suggestions.length > 0 && (
                            <div className="mt-6 pt-5 border-t border-border">
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="text-xl">💡</span>
                                    <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider">
                                        Suggested Alternatives
                                    </h3>
                                </div>
                                <div className="space-y-3">
                                    {suggestions.map((s, i) => (
                                        <div
                                            key={i}
                                            className="flex items-center justify-between p-3 rounded-lg bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800/50 transition-all hover:shadow-sm"
                                        >
                                            <div className="flex-1 min-w-0">
                                                <p className="text-sm font-medium text-foreground truncate">
                                                    {s.suggested_title}
                                                </p>
                                                <p className="text-xs text-muted-foreground mt-0.5">
                                                    {s.reason}
                                                </p>
                                            </div>
                                            <span className="ml-3 flex-shrink-0 inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300">
                                                ✓ {s.verification_probability}%
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Right: Gauge */}
                    <div className="flex-shrink-0">
                        <ProbabilityGauge
                            probability={result.verification_probability}
                            status={result.status}
                        />
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

const InfoRow = ({ label, value, bold }) => (
    <div className="space-y-1">
        <p className="text-xs text-muted-foreground uppercase tracking-wider">{label}</p>
        <p className={`text-sm ${bold ? "font-bold text-foreground" : "text-foreground"}`}>{value}</p>
    </div>
);

export default VerificationResults;

