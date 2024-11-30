// src/components/ThemeToggle.tsx
"use client";

import { Moon, Sun, Computer } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  const getIcon = () => {
    if (theme === "dark") return <Moon className="w-5 h-5 text-blue-400" />;
    if (theme === "light") return <Sun className="w-5 h-5 text-yellow-500" />;
    return <Computer className="w-5 h-5 text-gray-500" />;
  };

  const cycleTheme = () => {
    const themes = ["light", "dark", "system"];
    const currentIndex = themes.indexOf(theme ?? "system");
    const nextIndex = (currentIndex + 1) % themes.length;
    setTheme(themes[nextIndex]);
  };

  return (
    <button
      onClick={cycleTheme}
      className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
      title={`Current theme: ${theme}`}
    >
      {getIcon()}
    </button>
  );
}
