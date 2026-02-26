import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const ExplanationPanel = ({ explanation }) => {
    return (
        <Card className="border-border bg-card shadow-sm">
            <CardHeader>
                <CardTitle className="text-lg font-semibold text-foreground">
                    Reason for Decision
                </CardTitle>
            </CardHeader>
            <CardContent>
                <p className="text-sm text-muted-foreground leading-relaxed">{explanation}</p>
            </CardContent>
        </Card>
    );
};

export default ExplanationPanel;
