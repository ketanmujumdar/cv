// src/types/portfolio.ts
export interface Language {
  idiom: string;
  level: string;
}

export interface Interest {
  item: string;
  link?: string;
}

export interface ExperienceData {
  role: string;
  time: string;
  company: string;
  details: string;
}

export interface EducationData {
  degree: string;
  university: string;
  time: string;
}

export interface PortfolioData {
  sidebar: {
    about: boolean;
    education: boolean;
    name: string;
    tagline: string;
    avatar: string;
    email: string;
    phone: string;
    timezone: string;
    linkedin: string;
    pdf: string;
    languages: Language[];
    interests: Interest[];
  };
  "career-profile": {
    title: string;
    summary: string;
  };
  education: Education[];
  experiences: Experience[];
}
