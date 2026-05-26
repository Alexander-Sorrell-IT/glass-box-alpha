/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    optimizePackageImports: ["@rainbow-me/rainbowkit", "wagmi", "viem"],
  },
};

module.exports = nextConfig;
