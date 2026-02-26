import { CheckCircle2, XCircle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import ProbabilityGauge from "./ProbabilityGauge";

const VerificationResults = ({ result }) => {
    const isApproved = result.status === "Approved";

    return (
        <Card className="border-border bg-card shadow-sm">
            <CardContent className="p-6 md:p-8">
                <div className="flex flex-col md:flex-row gap-8 items-center md:items-start">
                    {/* Left: Info */}
                    <div className="flex-1 space-y-5 w-full">
                        <div className="flex flex-wrap items-center gap-3">
                            <h2 className="text-lg font-semibold text-foreground">Verification Result</h2>
                            <Badge
                                variant="outline"
                                className={`
                                    ${isApproved ? "border-success text-success bg-success/10" : ""}
                                    ${result.status === "Rejected" ? "border-destructive text-destructive bg-destructive/10" : ""}
                                    ${result.status === "Manual Review" ? "border-yellow-500 text-yellow-600 bg-yellow-500/10" : ""}
                                `}
                            >
                                {isApproved && <CheckCircle2 className="w-3 h-3 mr-1" />}
                                {result.status === "Rejected" && <XCircle className="w-3 h-3 mr-1" />}
                                {result.status === "Manual Review" && <div className="w-2 h-2 rounded-full bg-yellow-500 mr-2" />}
                                {result.status}
                            </Badge>
                            {result.metadata?.risk_tier && (
                                <Badge 
                                    variant="secondary" 
                                    className={`
                                        ${result.metadata.risk_tier === 'Critical' ? 'bg-red-500/20 text-red-500 border-red-500/50' : ''}
                                        ${result.metadata.risk_tier === 'High' ? 'bg-orange-500/20 text-orange-500 border-orange-500/50' : ''}
                                        ${result.metadata.risk_tier === 'Medium' ? 'bg-yellow-500/20 text-yellow-500 border-yellow-500/50' : ''}
                                        ${result.metadata.risk_tier === 'Low' ? 'bg-blue-500/20 text-blue-500 border-blue-500/50' : ''}
                                    `}
                                >
                                    Risk: {result.metadata.risk_tier}
                                </Badge>
                            )}
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
