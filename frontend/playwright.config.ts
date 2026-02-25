import { defineConfig, devices } from '@playwright/test'

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

const baseURL = process.env.BASE_URL || 'http://localhost:3000'

export default defineConfig({
  testDir: './e2e',
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
      command: isCI ? 'npm start' : 'npm run dev',
      url: 'http://localhost:3000',
      reuseExistingServer: true,
      timeout: 120 * 1000,
    },
  }),
})
