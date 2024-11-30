// src/components/sections/CareerProfile.tsx
interface CareerProfileProps {
  title: string;
  summary: string;
}

export default function CareerProfile({ title, summary }: CareerProfileProps) {
  return (
    <section className="bg-white rounded-xl shadow-lg p-8 backdrop-blur-lg bg-white/50">
      <h2 className="text-2xl font-bold mb-6 text-gray-900">{title}</h2>
      <p className="text-gray-700 leading-relaxed whitespace-pre-wrap text-lg">
        {summary}
      </p>
    </section>
  );
}
