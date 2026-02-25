// eslint-disable-next-line @typescript-eslint/no-require-imports
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  testPathIgnorePatterns: [
    '<rootDir>/node_modules/',
    '<rootDir>/.next/',
    '<rootDir>/e2e/',
  ],
  modulePathIgnorePatterns: [
    '<rootDir>/.next/',
  ],
  collectCoverageFrom: [
    '**/*.{js,jsx,ts,tsx}',
    '!**/*.d.ts',
    '!**/layout.tsx',
    '!**/loading.tsx',
    '!**/error.tsx',
    '!**/not-found.tsx',
    '!node_modules/**',
    '!.next/**',
    '!e2e/**',
    '!jest.config.js',
    '!jest.setup.js',
    '!playwright.config.ts',
    '!next.config.ts',
    '!postcss.config.mjs',
  ],
  coverageThreshold: {
    global: {
      branches: 30,
      functions: 30,
      lines: 30,
      statements: 30,
    },
  },
}

module.exports = createJestConfig(customJestConfig)
