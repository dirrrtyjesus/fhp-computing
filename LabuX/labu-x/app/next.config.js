/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        path: false,
        crypto: false,
        stream: false,
        http: false,
        https: false,
        zlib: false,
        util: false,
      };
    }

    // Ensure proper module resolution for Solana packages
    config.resolve.alias = {
      ...config.resolve.alias,
      '@solana/web3.js': require.resolve('@solana/web3.js'),
      '@solana/spl-token': require.resolve('@solana/spl-token'),
    };

    return config;
  },
};

module.exports = nextConfig;
