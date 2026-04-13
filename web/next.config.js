/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  basePath: process.env.NODE_ENV === 'production' ? '/kc-question-bank' : '',
  images: { unoptimized: true },
}

module.exports = nextConfig
