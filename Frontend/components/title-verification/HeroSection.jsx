import { TitleInput } from './TitleInput';

export function HeroSection({
  inputValue,
  onInputChange,
  onSubmit,
  isLoading,
}) {
  return (
    <section className="py-12 sm:py-16 px-4 text-center">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-4 text-balance">
          Title Similarity & Compliance Validation System
        </h1>

        <p className="text-lg text-muted-foreground mb-8">
          AI-powered verification and compliance system for newspaper title submissions
        </p>

        <form onSubmit={onSubmit} className="space-y-4">
          <TitleInput
            value={inputValue}
            onChange={onInputChange}
            disabled={isLoading}
            placeholder="Enter the newspaper title to verify"
          />

          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="w-full sm:w-auto px-8 py-3 bg-primary text-primary-foreground rounded-lg font-semibold hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                Verifying...
              </>
            ) : (
              'Verify Title'
            )}
          </button>
        </form>
      </div>
    </section>
  );
}
