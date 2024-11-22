/** @type {import('next').NextConfig} */
const nextConfig = {
    output: "export", // enable static exports -> next build will generate 'out' folder
    reactStrictMode: true,
    images: {
        unoptimized: true
    }
};

export default nextConfig;
