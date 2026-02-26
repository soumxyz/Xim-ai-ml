import { Search, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FlipWords } from "@/components/ui/flip-words";

const HeroSection = ({ title, onTitleChange, onVerify, isLoading }) => {
    const handleKeyDown = (e) => {
        if (e.key === "Enter" && title.trim() && !isLoading) {
            onVerify();
        }
    };

    const flipWords = ["Similarity", "Compliance", "Originality"];

    return (
        <section className="py-40 md:py-48 text-center">
            <div className="max-w-2xl mx-auto space-y-6">
                <h1 className="text-3xl md:text-4xl font-bold text-foreground tracking-tight leading-tight" style={{ fontWeight: 700, letterSpacing: '-0.025em' }}>
                    Title <FlipWords words={flipWords} duration={1500} /> Validation System
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
                            className="pl-10 h-12 rounded-full text-foreground placeholder:text-muted-foreground"
                            style={{
                                background: "rgba(255,255,255,0.15)",
                                backdropFilter: "blur(14px)",
                                WebkitBackdropFilter: "blur(14px)",
                                border: "1px solid rgba(255,255,255,0.35)",
                                boxShadow: "0 4px 24px rgba(0,0,0,0.08), inset 0 1px 0 rgba(255,255,255,0.4)",
                            }}
                        />
                    </div>
                    <Button
                        onClick={onVerify}
                        disabled={!title.trim() || isLoading}
                        className="h-12 px-8 font-semibold rounded-full text-gray-900"
                        style={{
                            background: "rgba(250, 189, 42, 0.75)",
                            backdropFilter: "blur(14px)",
                            WebkitBackdropFilter: "blur(14px)",
                            border: "1px solid rgba(252, 211, 77, 0.6)",
                            boxShadow: "0 4px 24px rgba(250, 189, 42, 0.25), inset 0 1px 0 rgba(255,255,255,0.4)",
                        }}
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
            </div>
        </section>
    );
};

export default HeroSection;
