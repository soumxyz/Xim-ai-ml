import { MessageSquare } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const ExplanationPanel = ({ explanation }) => {
    return (
        <Card className="border-border bg-card shadow-sm">
            <CardHeader>
                <CardTitle className="text-lg font-semibold text-foreground flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-primary" />
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
