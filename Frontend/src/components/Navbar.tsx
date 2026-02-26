import { Moon, Sun, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";

interface NavbarProps {
  darkMode: boolean;
  onToggleDarkMode: () => void;
}

const Navbar = ({ darkMode, onToggleDarkMode }: NavbarProps) => {
  return (
    <nav className="border-b border-border/50 bg-card/70 backdrop-blur-xl backdrop-saturate-150 sticky top-0 z-50">
      <div className="max-w-[1200px] mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-primary flex items-center justify-center">
            <Shield className="w-5 h-5 text-primary-foreground" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-semibold text-foreground leading-tight">Title Verification</span>
            <span className="text-xs text-muted-foreground leading-tight">Compliance System</span>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors hidden sm:block">
            About
          </a>
          <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors hidden sm:block">
            Documentation
          </a>
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
