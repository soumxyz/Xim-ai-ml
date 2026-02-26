import { Lightbulb } from 'lucide-react';

interface AIExplanationPanelProps {
  explanation: string;
}

export function AIExplanationPanel({ explanation }: AIExplanationPanelProps) {
  return (
    <div className="border-2 border-primary/30 rounded-lg p-6 bg-card">
      <div className="flex gap-3">
        <Lightbulb className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
        <div>
          <h3 className="font-semibold text-foreground mb-2">Reason for Decision</h3>
          <p className="text-sm leading-relaxed text-foreground">
            {explanation}
          </p>
        </div>
      </div>
    </div>
  );
}
