import { Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";

const Navbar = ({ darkMode, onToggleDarkMode }) => {
    return (
        <nav className="border-b border-border/50 bg-card/70 backdrop-blur-xl backdrop-saturate-150 sticky top-0 z-50">
            <div className="max-w-[1200px] mx-auto px-6 h-16 flex items-center justify-between">
                <div className="flex flex-col">
                    <span className="text-sm font-semibold text-foreground leading-tight">Title Verification</span>
                    <span className="text-xs text-muted-foreground leading-tight">Compliance System</span>
                </div>

                <div className="flex items-center">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={onToggleDarkMode}
                        className="rounded-lg"
                    >
                        {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                    </Button>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
