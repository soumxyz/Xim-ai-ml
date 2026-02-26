import {
    CheckCircle2,
    XCircle,
    Type,
    AudioLines,
    Brain,
    Ban,
    Clock,
    Combine,
    Tag,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

const DetailedAnalysis = ({ analysis }) => {
    const scores = [
        { label: "Lexical Similarity", value: analysis.lexical_similarity, icon: Type },
        { label: "Phonetic Similarity", value: analysis.phonetic_similarity, icon: AudioLines },
        { label: "Semantic Similarity", value: analysis.semantic_similarity, icon: Brain },
    ];

    const rules = [
        { label: "Disallowed Word Detection", passed: !analysis.disallowed_word, icon: Ban },
        { label: "Periodicity Rule Check", passed: !analysis.periodicity_violation, icon: Clock },
        { label: "Combination Detection", passed: !analysis.combination_violation, icon: Combine },
        { label: "Prefix/Suffix Rule Violation", passed: !analysis.prefix_suffix_violation, icon: Tag },
    ];

    return (
        <Card className="border-border bg-card shadow-sm">
            <CardHeader className="pb-4">
                <CardTitle className="text-lg font-semibold text-foreground">Detailed Analysis</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
                {/* Similarity Scores */}
                <div className="space-y-4">
                    <h4 className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
                        Similarity Scores
                    </h4>
                    <div className="space-y-3">
                        {scores.map((score) => (
                            <div key={score.label} className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <score.icon className="w-4 h-4 text-muted-foreground" />
                                    <span className="text-sm text-foreground">{score.label}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Progress value={score.value} className="h-1.5 w-20" />
                                    <span className="text-sm font-medium text-foreground w-10 text-right">{score.value}%</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Rule Checks */}
                <div className="space-y-3">
                    <h4 className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
                        Rule Compliance
                    </h4>
                    <div className="space-y-3">
                        {rules.map((rule) => (
                            <div
                                key={rule.label}
                                className="flex items-center justify-between"
                            >
                                <span className="text-sm text-foreground">{rule.label}</span>
                                {rule.passed ? (
                                    <CheckCircle2 className="w-4 h-4 text-success flex-shrink-0" />
                                ) : (
                                    <XCircle className="w-4 h-4 text-destructive flex-shrink-0" />
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

export default DetailedAnalysis;
