"use client";
// src/components/layout/Sidebar.tsx
import { useState, useEffect } from "react";
import { Clock, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { EducationData, Language, Interest } from "@/types/portfolio";
import { ThemeToggle } from "../ThemeToggle";

interface SidebarProps {
  timezone: string;
  languages: Language[];
  interests: Interest[];
  education: EducationData[];
}

export default function Sidebar({
  timezone,
  languages,
  interests,
  education,
}: SidebarProps) {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <aside className="md:col-span-1">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 space-y-8 backdrop-blur-lg">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <Clock className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <span className="text-gray-600 dark:text-gray-300">{timezone}</span>
          </div>
          <ThemeToggle />
        </div>

        {/* Education Section */}
        <div>
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            Education
          </h3>
          <div className="space-y-4">
            {education.map((edu, index) => (
              <div
                key={index}
                className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
              >
                <h4 className="font-medium text-gray-900 dark:text-white">
                  {edu.degree}
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  {edu.university}
                </p>
                <p className="text-sm text-blue-600 dark:text-blue-400">
                  {edu.time}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            Languages
          </h3>
          <ul className="space-y-3">
            {languages.map((lang) => (
              <li
                key={lang.idiom}
                className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
              >
                <span className="font-medium text-gray-900 dark:text-white">
                  {lang.idiom}
                </span>
                <span className="text-sm text-gray-600 dark:text-gray-300 px-3 py-1 bg-white dark:bg-gray-600 rounded-full">
                  {lang.level}
                </span>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            Interests
          </h3>
          <div className="flex flex-wrap gap-2">
            {interests.map((interest) => (
              <span
                key={interest.item}
                className="px-4 py-2 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full text-sm font-medium hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors"
              >
                {interest.item}
              </span>
            ))}
          </div>
        </div>
      </div>
    </aside>
  );
}
