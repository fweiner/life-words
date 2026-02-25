import { defineConfig, devices } from '@playwright/test'
import { MOCK_SUPABASE_URL } from './e2e/mock-auth-server'

const isCI = !!process.env.CI

const allProjects = [
  {
    name: 'chromium',
    use: { ...devices['Desktop Chrome'] },
  },
  {
    name: 'firefox',
    use: { ...devices['Desktop Firefox'] },
  },
  {
    name: 'webkit',
    use: { ...devices['Desktop Safari'] },
  },
  {
    name: 'Mobile Chrome',
    use: { ...devices['Pixel 5'] },
  },
  {
    name: 'Mobile Safari',
    use: { ...devices['iPhone 12'] },
  },
]

const ciProjects = [
  {
    name: 'chromium',
    use: { ...devices['Desktop Chrome'] },
  },
]

// Use a separate port for E2E to avoid conflicts with the dev server
const E2E_PORT = 3001
const baseURL = process.env.BASE_URL || `http://localhost:${E2E_PORT}`

export default defineConfig({
  testDir: './e2e',
  globalSetup: './e2e/global-setup.ts',
  globalTeardown: './e2e/global-teardown.ts',
  fullyParallel: true,
  forbidOnly: isCI,
  retries: isCI ? 2 : 0,
  workers: isCI ? 1 : undefined,
  reporter: 'html',
  timeout: 30_000,
  expect: {
    timeout: 10_000,
  },
  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: isCI ? ciProjects : allProjects,

  ...(!process.env.BASE_URL && {
    webServer: {
      command: `npx next build && npx next start -p ${E2E_PORT}`,
      url: `http://localhost:${E2E_PORT}`,
      reuseExistingServer: !isCI,
      timeout: 120 * 1000,
      env: {
        NEXT_PUBLIC_SUPABASE_URL: MOCK_SUPABASE_URL,
        NEXT_PUBLIC_SUPABASE_ANON_KEY: 'e2e-mock-anon-key',
      },
    },
  }),
})
