/** @type {import('next').NextConfig} */



const isProd = process.env.NODE_ENV === 'production';
const nextConfig = {
  reactStrictMode: true,
  images: {
    unoptimized: true, // Disable default image optimization
  },
  assetPrefix: isProd ? 'https://tamlt2704.github.io/' : '',
  basePath: isProd ? '/tamlt2704.github.io' : '',
  output: 'export'
};

module.exports = nextConfig;
// export default nextConfig;
