import { Search, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const HeroSection = ({ title, onTitleChange, onVerify, isLoading }) => {
    const handleKeyDown = (e) => {
        if (e.key === "Enter" && title.trim() && !isLoading) {
            onVerify();
        }
    };

    return (
        <section className="py-14 md:py-20 text-center">
            <div className="max-w-2xl mx-auto space-y-6">
                <h1 className="text-3xl md:text-4xl font-bold text-foreground tracking-tight leading-tight" style={{ fontWeight: 700, letterSpacing: '-0.025em' }}>
                    Title Similarity &<br />Compliance Validation System
                </h1>
                <p className="text-muted-foreground text-base md:text-lg">
                    AI-powered Title Verification and Compliance System
                </p>

                <div className="flex flex-col sm:flex-row gap-3 max-w-xl mx-auto pt-4">
                    <div className="relative flex-1">
                        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <Input
                            value={title}
                            onChange={(e) => onTitleChange(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Enter newspaper title to verify..."
                            className="pl-10 h-12 bg-card border-border text-foreground placeholder:text-muted-foreground rounded-full shadow-sm"
                        />
                    </div>
                    <Button
                        onClick={onVerify}
                        disabled={!title.trim() || isLoading}
                        className="h-12 px-8 bg-primary text-primary-foreground hover:bg-navy-light font-semibold rounded-full shadow-sm"
                    >
                        {isLoading ? (
                            <>
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                Verifying
                            </>
                        ) : (
                            "Verify Title"
                        )}
                    </Button>
                </div>

                <p className="text-xs text-muted-foreground">
                    Checks similarity, rule violations, and approval probability
                </p>
            </div>
        </section>
    );
};

export default HeroSection;
