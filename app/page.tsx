'use client';

import { useEffect, useRef, useState } from 'react';
import { verifyTitle } from '@/lib/mockApi';
import { RecentCheck, VerificationResult } from '@/lib/types';
import { TopNavBar } from '@/components/title-verification/TopNavBar';
import { HeroSection } from '@/components/title-verification/HeroSection';
import { VerificationResults } from '@/components/title-verification/VerificationResults';
import { RecentChecksPanel } from '@/components/title-verification/RecentChecksPanel';

export default function Home() {
  const [inputValue, setInputValue] = useState('');
  const [results, setResults] = useState<VerificationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [recentChecks, setRecentChecks] = useState<RecentCheck[]>([]);
  const resultsRef = useRef<HTMLDivElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    setIsLoading(true);
    try {
      const result = await verifyTitle(inputValue);
      setResults(result);

      // Add to recent checks
      const newCheck: RecentCheck = {
        id: Date.now().toString(),
        title: inputValue,
        status: result.status,
        probability: result.verification_probability,
        timestamp: new Date(),
      };
      setRecentChecks((prev) => [newCheck, ...prev.slice(0, 9)]);

      // Scroll to results
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (error) {
      console.error('Verification error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <TopNavBar />

      <main className="mx-auto max-w-7xl">
        <HeroSection
          inputValue={inputValue}
          onInputChange={setInputValue}
          onSubmit={handleSubmit}
          isLoading={isLoading}
        />

        {results && (
          <div ref={resultsRef} className="space-y-12 pb-12">
            <div className="px-4">
              <VerificationResults result={results} />
            </div>

            {recentChecks.length > 0 && (
              <div className="px-4">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  <div className="lg:col-span-2" />
                  <RecentChecksPanel checks={recentChecks} />
                </div>
              </div>
            )}
          </div>
        )}

        {!results && recentChecks.length > 0 && (
          <div className="px-4 py-12">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-4xl mx-auto">
              <div className="lg:col-span-2" />
              <RecentChecksPanel checks={recentChecks} />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
