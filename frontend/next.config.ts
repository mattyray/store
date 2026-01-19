import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  images: {
    // Enable optimization - serves WebP/AVIF at appropriate sizes
    // Original quality preserved, just smarter delivery
    formats: ['image/avif', 'image/webp'],
    // High quality for photography - visually lossless
    // quality is set per-image via the Image component, default is 75
    // We'll use 90 on individual images for photography
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'matthewraynor-store.s3.amazonaws.com',
      },
      {
        protocol: 'https',
        hostname: 'matthewraynor-store.s3.us-east-2.amazonaws.com',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
      },
    ],
  },
};

export default nextConfig;
