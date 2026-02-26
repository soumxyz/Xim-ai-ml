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
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "@/components/ui/accordion";
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
            <Accordion type="single" collapsible defaultValue="analysis">
                <AccordionItem value="analysis" className="border-none">
                    <CardHeader className="pb-0">
                        <AccordionTrigger className="hover:no-underline py-0">
                            <CardTitle className="text-lg font-semibold text-foreground">Detailed Analysis</CardTitle>
                        </AccordionTrigger>
                    </CardHeader>
                    <AccordionContent>
                        <CardContent className="pt-4 space-y-6">
                            {/* Similarity Scores */}
                            <div className="space-y-4">
                                <h4 className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
                                    Similarity Scores
                                </h4>
                                <div className="space-y-3">
                                    {scores.map((score) => (
                                        <div key={score.label} className="space-y-1.5">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-2">
                                                    <score.icon className="w-4 h-4 text-muted-foreground" />
                                                    <span className="text-sm text-foreground">{score.label}</span>
                                                </div>
                                                <span className="text-sm font-medium text-foreground">{score.value}%</span>
                                            </div>
                                            <Progress value={score.value} className="h-1.5" />
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Rule Checks */}
                            <div className="space-y-3">
                                <h4 className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
                                    Rule Compliance
                                </h4>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                    {rules.map((rule) => (
                                        <div
                                            key={rule.label}
                                            className="flex items-center gap-3 p-3 rounded-lg bg-muted/50"
                                        >
                                            {rule.passed ? (
                                                <CheckCircle2 className="w-4 h-4 text-success flex-shrink-0" />
                                            ) : (
                                                <XCircle className="w-4 h-4 text-destructive flex-shrink-0" />
                                            )}
                                            <span className="text-sm text-foreground">{rule.label}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </CardContent>
                    </AccordionContent>
                </AccordionItem>
            </Accordion>
        </Card>
    );
};

export default DetailedAnalysis;
