import { useState, useRef, useEffect } from "react";
import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import VerificationResults from "@/components/VerificationResults";
import DetailedAnalysis from "@/components/DetailedAnalysis";
import ExplanationPanel from "@/components/ExplanationPanel";
import RecentChecks from "@/components/RecentChecks";
import { getMockResult, recentChecks as initialChecks } from "@/lib/mockData";
import { toast } from "sonner"; // Assuming sonner is available for error reporting

const Index = () => {
    const [title, setTitle] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [darkMode, setDarkMode] = useState(false);
    const [checks, setChecks] = useState(initialChecks);
    const resultsRef = useRef(null);

    useEffect(() => {
        document.documentElement.classList.toggle("dark", darkMode);
    }, [darkMode]);

    const handleTitleChange = (newTitle) => {
        setTitle(newTitle);
        if (!newTitle.trim()) {
            setResult(null);
        }
    };

    const handleVerify = async () => {
        setIsLoading(true);
        setResult(null);

        try {
            const response = await fetch("http://localhost:8000/api/v1/verify/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ title }),
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
                similarity_score: Math.round((1 - data.verification_probability/100) * 100) // Fallback calculation
            };
            
            // In fact, the backend now returns exactly what we need
            setResult(data);
            
            const newCheck = {
                title: title,
                status: data.decision === "Accept" ? "Approved" : "Rejected",
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
        <div className="min-h-screen bg-background">
            <Navbar darkMode={darkMode} onToggleDarkMode={() => setDarkMode(!darkMode)} />

            <main className="max-w-[1200px] mx-auto px-6">
                <HeroSection
                    title={title}
                    onTitleChange={handleTitleChange}
                    onVerify={handleVerify}
                    isLoading={isLoading}
                />

                {(result || isLoading) && (
                    <div ref={resultsRef} className="pb-16 space-y-6">
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
    );
};

export default Index;
