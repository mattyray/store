import type { NextConfig } from "next";
import { withSentryConfig } from "@sentry/nextjs";

const nextConfig: NextConfig = {
  reactCompiler: true,
  images: {
    // Disable private IP blocking for local Docker development
    unoptimized: process.env.NODE_ENV === 'development',
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
        port: '7974',
      },
      {
        protocol: 'http',
        hostname: 'backend',
        port: '7974',
      },
    ],
  },
};

export default withSentryConfig(nextConfig, {
  org: "matthew-raynor",
  project: "store-nextjs",
  silent: !process.env.CI,
  widenClientFileUpload: true,
  disableLogger: true,
});
