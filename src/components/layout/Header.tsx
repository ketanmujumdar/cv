// src/components/layout/Header.tsx
import { Mail, Phone, Linkedin, FileText } from "lucide-react";

interface HeaderProps {
  name: string;
  tagline: string;
  email: string;
  phone: string;
  linkedin: string;
  pdf: string;
}
// src/components/layout/Header.tsx
export default function Header({
  name,
  tagline,
  email,
  phone,
  linkedin,
  pdf,
}: HeaderProps) {
  return (
    <header className="relative bg-black text-white">
      <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 opacity-90" />
      <div className="relative container mx-auto px-6 py-20">
        <div className="flex flex-col md:flex-row items-center">
          <div className="w-full text-center md:text-left">
            <h1 className="text-5xl font-bold mb-4">{name}</h1>
            <p className="text-2xl text-gray-200 mb-8">{tagline}</p>
            <div className="flex flex-wrap gap-4 justify-center md:justify-start">
              <a
                href={`mailto:${email}`}
                className="transform hover:scale-105 transition-all duration-200 bg-white/10 backdrop-blur-md px-6 py-3 rounded-full flex items-center gap-2 hover:bg-white/20"
              >
                <Mail className="w-4 h-4" />
                <span>Email</span>
              </a>
              <a
                href={`tel:${phone}`}
                className="transform hover:scale-105 transition-all duration-200 bg-white/10 backdrop-blur-md px-6 py-3 rounded-full flex items-center gap-2 hover:bg-white/20"
              >
                <Phone className="w-4 h-4" />
                <span>Call</span>
              </a>
              <a
                href={linkedin}
                target="_blank"
                rel="noopener noreferrer"
                className="transform hover:scale-105 transition-all duration-200 bg-white text-blue-600 px-6 py-3 rounded-full flex items-center gap-2 hover:bg-gray-100"
              >
                <Linkedin className="w-4 h-4" />
                <span>LinkedIn</span>
              </a>
              <a
                href={pdf}
                target="_blank"
                rel="noopener noreferrer"
                className="transform hover:scale-105 transition-all duration-200 bg-white/10 backdrop-blur-md px-6 py-3 rounded-full flex items-center gap-2 hover:bg-white/20"
              >
                <FileText className="w-4 h-4" />
                <span>Resume</span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
