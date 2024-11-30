// src/lib/yaml.ts
import { readFileSync } from 'fs';
import { join } from 'path';
import yaml from 'js-yaml';
import { PortfolioData } from '@/types/portfolio';

export function getPortfolioData(): PortfolioData {
  try {
    const yamlFile = join(process.cwd(), 'src', 'data', 'portfolio.yaml');
    const fileContents = readFileSync(yamlFile, 'utf8');
    return yaml.load(fileContents) as PortfolioData;
  } catch (error) {
    console.error('Error loading portfolio data:', error);
    // Return a default/empty data structure if file not found
    return {
      sidebar: {
        about: false,
        education: true,
        name: "",
        tagline: "",
        avatar: "",
        email: "",
        phone: "",
        timezone: "",
        linkedin: "",
        pdf: "",
        languages: [],
        interests: []
      },
      "career-profile": {
        title: "",
        summary: ""
      },
      education: [],
      experiences: []
    };
  }
}