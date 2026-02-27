import { useState, useRef, useEffect } from "react";
import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import VerificationResults from "@/components/VerificationResults";
import DetailedAnalysis from "@/components/DetailedAnalysis";
import ExplanationPanel from "@/components/ExplanationPanel";
import RecentChecks from "@/components/RecentChecks";
import { getMockResult, recentChecks as initialChecks } from "@/lib/mockData";
import { toast } from "sonner";
import { useTalkback, playTing } from "@/hooks/useTalkback";

const Index = () => {
    const [title, setTitle] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [darkMode, setDarkMode] = useState(false);
    const [highContrast, setHighContrast] = useState(false);
    const [talkBack, setTalkBack] = useState(false);
    const [checks, setChecks] = useState(initialChecks);
    const resultsRef = useRef(null);

    useTalkback(talkBack);

    useEffect(() => {
        document.documentElement.classList.toggle("dark", darkMode);
        document.documentElement.classList.toggle("high-contrast", highContrast);
    }, [darkMode, highContrast]);

    // 4 rapid spacebar presses toggles TalkBack
    useEffect(() => {
        let count = 0;
        let resetTimer = null;

        const onKey = (e) => {
            // Ignore spacebar in text inputs
            const tag = e.target?.tagName?.toLowerCase();
            if (tag === "input" || tag === "textarea") return;
            if (e.code !== "Space") { count = 0; return; }

            e.preventDefault();
            count += 1;
            clearTimeout(resetTimer);

            if (count >= 4) {
                count = 0;
                setTalkBack((prev) => !prev);
                return;
            }

            // Reset if no spacebar within 1s
            resetTimer = setTimeout(() => { count = 0; }, 1000);
        };

        document.addEventListener("keydown", onKey);
        return () => {
            document.removeEventListener("keydown", onKey);
            clearTimeout(resetTimer);
        };
    }, []);

    const handleTitleChange = (newTitle) => {
        setTitle(newTitle);
        if (!newTitle.trim()) {
            setResult(null);
        }
    };

    const handleVerify = async (overrideTitle) => {
        const verifyTitle = overrideTitle || title;
        setIsLoading(true);
        setResult(null);

        try {
            const response = await fetch("http://localhost:8000/api/v1/verify/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ title: verifyTitle }),
            });

            if (!response.ok) {
                throw new Error("Verification failed at server");
            }

            const data = await response.json();

            // Map backend score keys if they differ slightly from UI (already handled in orchestrator update)
            const apiResult = {
                ...data,
                submitted_title: title,
                closest_match: data.metadata?.best_match || "None",
                similarity_score: Math.round((1 - data.verification_probability / 100) * 100) // Fallback calculation
            };

            // In fact, the backend now returns exactly what we need
            setResult(data);
            if (talkBack) playTing();

            const newCheck = {
                title: verifyTitle,
                status: data.decision === "Accept" ? "Approved" :
                    data.decision === "Manual Review" ? "Manual Review" : "Rejected",
                probability: data.verification_probability,
                timestamp: "Just now"
            };
            setChecks((prev) => [newCheck, ...prev]);
        } catch (error) {
            console.error("API Error:", error);
            toast.error("Could not connect to verification server.");
        } finally {
            setIsLoading(false);
            setTimeout(() => {
                resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
            }, 100);
        }
    };

    const handleClearAll = () => {
        setChecks([]);
    };

    return (
        <div className="min-h-screen bg-white dark:bg-background relative">
            {/* Light-mode diagonal cross grid background */}
            <div
                className="absolute inset-0 z-0 dark:hidden"
                style={{
                    backgroundImage: `
                        linear-gradient(45deg, transparent 49%, #e5e7eb 49%, #e5e7eb 51%, transparent 51%),
                        linear-gradient(-45deg, transparent 49%, #e5e7eb 49%, #e5e7eb 51%, transparent 51%)
                    `,
                    backgroundSize: "40px 40px",
                    WebkitMaskImage:
                        "radial-gradient(ellipse 100% 80% at 50% 100%, #000 50%, transparent 90%)",
                    maskImage:
                        "radial-gradient(ellipse 100% 80% at 50% 100%, #000 50%, transparent 90%)",
                }}
            />
            {/* Dark-mode black grid background */}
            <div
                className="absolute inset-0 z-0 hidden dark:block"
                style={{
                    background: "#000000",
                    backgroundImage: `
                        linear-gradient(to right, rgba(75, 85, 99, 0.4) 1px, transparent 1px),
                        linear-gradient(to bottom, rgba(75, 85, 99, 0.4) 1px, transparent 1px)
                    `,
                    backgroundSize: "40px 40px",
                }}
            />
            <div className="relative z-10">
                <Navbar
                    darkMode={darkMode}
                    onToggleDarkMode={() => setDarkMode(!darkMode)}
                    highContrast={highContrast}
                    onToggleHighContrast={() => setHighContrast(!highContrast)}
                    talkBack={talkBack}
                    onToggleTalkBack={() => setTalkBack(!talkBack)}
                />

                <main className="max-w-[1200px] mx-auto px-6">
                    <HeroSection
                        title={title}
                        onTitleChange={handleTitleChange}
                        onVerify={handleVerify}
                        isLoading={isLoading}
                    />

                    {/* Suggested Alternatives — directly below input */}
                    {result?.suggestions && result.suggestions.length > 0 && (
                        <div className="max-w-2xl mx-auto -mt-36 mb-8 relative z-20">
                            <div
                                className="rounded-2xl p-5 text-center"
                                style={{
                                    background: "rgba(255,255,255,0.06)",
                                    backdropFilter: "blur(16px)",
                                    WebkitBackdropFilter: "blur(16px)",
                                    border: "1px solid rgba(255,255,255,0.15)",
                                    boxShadow: "0 8px 32px rgba(0,0,0,0.1), inset 0 1px 0 rgba(255,255,255,0.1)",
                                }}
                            >
                                <div className="flex items-center justify-center gap-2 mb-4">
                                    <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-widest">
                                        Suggested Alternatives
                                    </h3>
                                </div>
                                <div className="flex flex-wrap items-center justify-center gap-2">
                                    {result.suggestions.map((s, i) => (
                                        <button
                                            key={i}
                                            onClick={() => {
                                                setTitle(s.suggested_title);
                                                handleVerify(s.suggested_title);
                                            }}
                                            className="text-sm text-foreground transition-all cursor-pointer hover:scale-105"
                                            style={{
                                                padding: "8px 18px",
                                                borderRadius: "9999px",
                                                background: "rgba(255,255,255,0.1)",
                                                backdropFilter: "blur(14px)",
                                                WebkitBackdropFilter: "blur(14px)",
                                                border: "1px solid rgba(255,255,255,0.2)",
                                                boxShadow: "0 2px 12px rgba(0,0,0,0.06), inset 0 1px 0 rgba(255,255,255,0.15)",
                                            }}
                                        >
                                            {s.suggested_title}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {(result || isLoading) && (
                        <div ref={resultsRef} className="pb-6 space-y-6">
                            {result && (
                                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                                    <div className="lg:col-span-2 space-y-6">
                                        <VerificationResults result={{
                                            ...result,
                                            status: result.decision === "Accept" ? "Approved" : "Rejected",
                                            submitted_title: title,
                                            closest_match: result.metadata?.best_match || "None",
                                            similarity_score: result.analysis ? Math.max(result.analysis.lexical_similarity, result.analysis.phonetic_similarity, result.analysis.semantic_similarity) : 0
                                        }} />
                                        <DetailedAnalysis analysis={{
                                            ...result.analysis,
                                            dominant_signal: result.metadata?.dominant_signal
                                        }} />
                                    </div>
                                    <div className="space-y-6">
                                        <ExplanationPanel explanation={result.explanation} />
                                        {checks.length > 0 && <RecentChecks checks={checks} onClearAll={handleClearAll} />}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                </main>
            </div>
        </div>
    );
};

export default Index;
