import { VerificationResult } from '@/lib/types';
import { ProbabilityVisualization } from './ProbabilityVisualization';
import { DetailedAnalysisSection } from './DetailedAnalysisSection';
import { AIExplanationPanel } from './AIExplanationPanel';
import { StatusBadge } from './StatusBadge';

interface VerificationResultsProps {
  result: VerificationResult;
}

export function VerificationResults({ result }: VerificationResultsProps) {
  return (
    <section className="py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-card border border-border rounded-lg p-8 space-y-8">
          {/* Header */}
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Submitted Title</p>
                <h2 className="text-2xl font-bold text-foreground">
                  {result.submitted_title}
                </h2>
              </div>
              <StatusBadge status={result.status} size="lg" />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-border">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Closest Match</p>
                <p className="text-lg font-semibold text-foreground">
                  {result.closest_match}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Similarity Score</p>
                <p className="text-lg font-semibold text-foreground">
                  {result.similarity_score}%
                </p>
              </div>
            </div>
          </div>

          {/* Probability Visualization */}
          <div className="flex justify-center py-4">
            <ProbabilityVisualization
              probability={result.verification_probability}
              status={result.status}
            />
          </div>

          {/* Explanation */}
          <AIExplanationPanel explanation={result.explanation} />

          {/* Detailed Analysis */}
          <DetailedAnalysisSection analysis={result.analysis} />
        </div>
      </div>
    </section>
  );
}
