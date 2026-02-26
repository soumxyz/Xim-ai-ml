'use client';

import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { VerificationAnalysis } from '@/lib/types';
import { AnalysisItem } from './AnalysisItem';
import { cn } from '@/lib/utils';

interface DetailedAnalysisSectionProps {
  analysis: VerificationAnalysis;
}

export function DetailedAnalysisSection({ analysis }: DetailedAnalysisSectionProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border border-border rounded-lg overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-6 py-4 bg-muted hover:bg-muted/70 transition-colors"
      >
        <h3 className="text-lg font-semibold text-foreground">Detailed Analysis</h3>
        <ChevronDown
          className={cn(
            'w-5 h-5 text-foreground transition-transform',
            isOpen && 'rotate-180'
          )}
        />
      </button>

      {isOpen && (
        <div className="bg-card">
          <AnalysisItem
            label="Lexical Similarity"
            value={analysis.lexical_similarity}
            isPercentage
          />
          <AnalysisItem
            label="Phonetic Similarity"
            value={analysis.phonetic_similarity}
            isPercentage
          />
          <AnalysisItem
            label="Semantic Similarity"
            value={analysis.semantic_similarity}
            isPercentage
          />
          <AnalysisItem
            label="Disallowed Word Detection"
            value={analysis.disallowed_word}
          />
          <AnalysisItem
            label="Periodicity Rule Violation"
            value={analysis.periodicity_violation}
          />
          <AnalysisItem
            label="Combination Detection"
            value={analysis.combination_violation}
          />
          <AnalysisItem
            label="Prefix/Suffix Violation"
            value={analysis.prefix_suffix_violation}
          />
        </div>
      )}
    </div>
  );
}
