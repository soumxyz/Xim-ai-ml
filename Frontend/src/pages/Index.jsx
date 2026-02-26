import { useState, useRef, useEffect } from "react";
import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import VerificationResults from "@/components/VerificationResults";
import DetailedAnalysis from "@/components/DetailedAnalysis";
import ExplanationPanel from "@/components/ExplanationPanel";
import RecentChecks from "@/components/RecentChecks";
import { getMockResult, recentChecks as initialChecks } from "@/lib/mockData";

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

    const handleVerify = async () => {
        setIsLoading(true);
        setResult(null);

        await new Promise((resolve) => setTimeout(resolve, 1500));

        const mockResult = getMockResult(title);
        setResult(mockResult);
        setIsLoading(false);

        setTimeout(() => {
            resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
        }, 100);
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
                    onTitleChange={setTitle}
                    onVerify={handleVerify}
                    isLoading={isLoading}
                />

                {(result || isLoading) && (
                    <div ref={resultsRef} className="pb-16 space-y-6">
                        {result && (
                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                                <div className="lg:col-span-2 space-y-6">
                                    <VerificationResults result={result} />
                                    <DetailedAnalysis analysis={result.analysis} />
                                    <ExplanationPanel explanation={result.explanation} />
                                </div>
                                <div>
                                    <RecentChecks checks={checks} onClearAll={handleClearAll} />
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {!result && !isLoading && (
                    <div className="pb-16">
                        <div className="max-w-md mx-auto">
                            <RecentChecks checks={checks} onClearAll={handleClearAll} />
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
};

export default Index;
