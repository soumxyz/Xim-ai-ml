import { cn } from '@/lib/utils';

export function TitleInput({
  value,
  onChange,
  disabled = false,
  placeholder = "Enter the newspaper title to verify",
}) {
  return (
    <div className="w-full">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder={placeholder}
        className={cn(
          "w-full px-4 py-3 rounded-lg border-2 border-border bg-input text-foreground",
          "placeholder:text-muted-foreground focus:outline-none focus:border-primary transition-colors",
          "text-base font-normal",
          disabled && "opacity-60 cursor-not-allowed bg-muted"
        )}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            e.currentTarget.form?.requestSubmit();
          }
        }}
      />
      <p className="text-sm text-muted-foreground mt-2">
        Enter a newspaper title to check for compliance and similarity with existing registrations.
      </p>
    </div>
  );
}
