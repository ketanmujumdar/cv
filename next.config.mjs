// next.config.mjs
/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'export',
    images: {
      unoptimized: true,
    },
    basePath: '/portfolio-website',
    rewrites: async () => {
      return [
        {
          source: '/',
          destination: '/index'
        }
      ];
    }
  };
  
  export default nextConfig;