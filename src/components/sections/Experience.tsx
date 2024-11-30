// src/components/sections/Experience.tsx
import { ExperienceData } from "@/types/portfolio";

interface ExperienceProps {
  experiences: ExperienceData[];
}

export default function Experience({ experiences }: ExperienceProps) {
  return (
    <section className="bg-white rounded-xl shadow-lg p-8 backdrop-blur-lg bg-white/50">
      <h2 className="text-2xl font-bold mb-8 text-gray-900">Experience</h2>
      <div className="space-y-12">
        {experiences.map((exp, index) => (
          <div
            key={index}
            className="relative pl-8 before:absolute before:left-0 before:top-0 before:bottom-0 before:w-1 before:bg-gradient-to-b before:from-blue-600 before:to-purple-600 before:rounded-full"
          >
            <div className="absolute left-0 top-0 w-2 h-2 bg-blue-600 rounded-full transform -translate-x-[3px]" />
            <h3 className="text-xl font-bold text-gray-900 mb-2">{exp.role}</h3>
            <p className="text-blue-600 font-medium mb-4">
              {exp.company} | {exp.time}
            </p>
            <div className="text-gray-700 whitespace-pre-wrap prose prose-blue max-w-none">
              {exp.details}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
