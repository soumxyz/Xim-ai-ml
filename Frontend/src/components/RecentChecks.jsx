import { CheckCircle2, XCircle, History, Trash2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const RecentChecks = ({ checks, onClearAll }) => {
    return (
        <Card className="border-border bg-card shadow-sm backdrop-blur-xl">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-lg font-semibold text-foreground flex items-center gap-2">
                    <History className="w-5 h-5 text-primary" />
                    Recent Verifications
                </CardTitle>
                {checks.length > 0 && onClearAll && (
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={onClearAll}
                        className="text-destructive hover:text-destructive hover:bg-destructive/10 text-xs gap-1.5 rounded-full px-3"
                    >
                        <Trash2 className="w-3.5 h-3.5" />
                        Clear All
                    </Button>
                )}
            </CardHeader>
            <CardContent className="space-y-0.5">
                {checks.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-8">
                        No recent verifications
                    </p>
                ) : (
                    checks.map((check, i) => (
                        <div
                            key={i}
                            className="flex items-center justify-between py-3 border-b border-border/50 last:border-0 rounded-xl px-2 hover:bg-muted/50 transition-colors"
                        >
                            <div className="flex items-center gap-3 min-w-0">
                                {check.status === "Approved" ? (
                                    <CheckCircle2 className="w-4 h-4 text-success flex-shrink-0" />
                                ) : (
                                    <XCircle className="w-4 h-4 text-destructive flex-shrink-0" />
                                )}
                                <div className="min-w-0">
                                    <p className="text-sm text-foreground truncate">{check.title}</p>
                                    <p className="text-xs text-muted-foreground">{check.timestamp}</p>
                                </div>
                            </div>
                            <span className="text-sm font-medium text-muted-foreground ml-3">
                                {check.probability}%
                            </span>
                        </div>
                    ))
                )}
            </CardContent>
        </Card>
    );
};

export default RecentChecks;
