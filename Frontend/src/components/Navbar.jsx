import { Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";

const Navbar = ({ darkMode, onToggleDarkMode, highContrast, onToggleHighContrast }) => {
    return (
        <nav className="border-b border-border/50 bg-card/70 backdrop-blur-xl backdrop-saturate-150 sticky top-0 z-50">
            <div className="max-w-[1200px] mx-auto px-6 h-16 flex items-center justify-between">
                <div className="flex flex-col">
                    <span className="text-sm font-semibold text-foreground leading-tight">Title Verification</span>
                    <span className="text-xs text-muted-foreground leading-tight">Compliance System</span>
                </div>

                <div className="flex items-center gap-3">
                    {/* High contrast toggle switch */}
                    <button
                        type="button"
                        onClick={onToggleHighContrast}
                        title={highContrast ? "Disable high contrast" : "Enable high contrast"}
                        className="flex items-center gap-2 focus:outline-none"
                        aria-pressed={highContrast}
                    >
                        <span className="text-xs font-semibold text-muted-foreground select-none">HC</span>
                        <div
                            className="relative w-10 h-5 rounded-full transition-colors duration-300"
                            style={{
                                background: highContrast ? "hsl(45 100% 45%)" : "hsl(var(--muted))",
                                border: "1.5px solid",
                                borderColor: highContrast ? "hsl(45 100% 38%)" : "hsl(var(--border))",
                            }}
                        >
                            <span
                                className="absolute top-1/2 w-4 h-4 rounded-full shadow transition-transform duration-300"
                                style={{
                                    left: "2px",
                                    transform: `translateX(${highContrast ? "18px" : "0px"}) translateY(-50%)`,
                                    background: highContrast ? "#000" : "hsl(var(--foreground))",
                                }}
                            />
                        </div>
                    </button>

                    {/* Dark mode toggle */}
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={onToggleDarkMode}
                        className="rounded-lg text-foreground hover:text-foreground hover:bg-muted"
                    >
                        {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                    </Button>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;

