import { CheckCircle2, XCircle, FileText, Copy } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { VerificationResult } from "@/lib/mockData";
import ProbabilityGauge from "./ProbabilityGauge";

interface Props {
  result: VerificationResult;
}

const VerificationResults = ({ result }: Props) => {
  const isApproved = result.status === "Approved";

  return (
    <Card className="border-border bg-card shadow-sm">
      <CardContent className="p-6 md:p-8">
        <div className="flex flex-col md:flex-row gap-8 items-center md:items-start">
          {/* Left: Info */}
          <div className="flex-1 space-y-5 w-full">
            <div className="flex items-center gap-3">
              <h2 className="text-lg font-semibold text-foreground">Verification Result</h2>
              <Badge
                variant="outline"
                className={
                  isApproved
                    ? "border-success text-success bg-success/10"
                    : "border-destructive text-destructive bg-destructive/10"
                }
              >
                {isApproved ? (
                  <CheckCircle2 className="w-3 h-3 mr-1" />
                ) : (
                  <XCircle className="w-3 h-3 mr-1" />
                )}
                {result.status}
              </Badge>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <InfoRow label="Submitted Title" value={result.submitted_title} />
              <InfoRow label="Closest Match" value={result.closest_match} />
              <InfoRow label="Similarity Score" value={`${result.similarity_score}%`} />
              <InfoRow
                label="Verification Probability"
                value={`${result.verification_probability}%`}
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

const InfoRow = ({ label, value, bold }: { label: string; value: string; bold?: boolean }) => (
  <div className="space-y-1">
    <p className="text-xs text-muted-foreground uppercase tracking-wider">{label}</p>
    <p className={`text-sm ${bold ? "font-bold text-foreground" : "text-foreground"}`}>{value}</p>
  </div>
);

export default VerificationResults;
