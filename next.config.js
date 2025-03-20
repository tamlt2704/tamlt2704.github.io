/** @type {import('next').NextConfig} */



const isProd = process.env.NODE_ENV === 'production';
const nextConfig = {
  reactStrictMode: true,
  images: {
    unoptimized: true, // Disable default image optimization
  },
  assetPrefix: isProd ? '' : '',
  basePath: isProd ? '' : '',
  output: 'export'
};

module.exports = nextConfig;
// export default nextConfig;
