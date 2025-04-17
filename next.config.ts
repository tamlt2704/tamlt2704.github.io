import type { NextConfig } from "next";
import createMDX from '@next/mdx';

const nextConfig: NextConfig = {
  // Configure `pageExtensions` to include MDX files
  pageExtensions: ['js', 'jsx', 'mdx', 'ts', 'tsx'],
  output: 'export',
  basePath: '',
  images: {
    unoptimized: true
  }
};

const withMDX = createMDX({
  // Add markdown plugins here, as desired
})

// export default nextConfig;
module.exports = withMDX(nextConfig)
