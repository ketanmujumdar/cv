// src/app/page.tsx
import { getPortfolioData } from "@/lib/yaml";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import CareerProfile from "@/components/sections/CareerProfile";
import Experience from "@/components/sections/Experience";

export default function Home() {
  const data = getPortfolioData();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header {...data.sidebar} />

      <main className="container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Sidebar
            timezone={data.sidebar.timezone}
            languages={data.sidebar.languages}
            interests={data.sidebar.interests}
            education={data.education} // Pass education to Sidebar
          />

          <div className="md:col-span-2 space-y-8">
            <CareerProfile
              title={data["career-profile"].title}
              summary={data["career-profile"].summary}
            />
            <Experience experiences={data.experiences} />
          </div>
        </div>
      </main>
    </div>
  );
}
