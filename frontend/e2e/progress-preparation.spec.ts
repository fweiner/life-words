import { test, expect } from '@playwright/test'
import { mockAuth } from './fixtures/test-helpers'

const mockProfile = {
  id: 'e2e-test-user-id',
  email: 'e2e-test@example.com',
  first_name: 'Test',
  role: 'patient',
}

const mockProgress = {
  summary: {
    total_sessions: 3,
    name_practice: {
      sessions: 1,
      correct: 4,
      total: 5,
      accuracy: 80,
      avg_response_time_sec: 3.2,
      avg_speech_confidence: 85,
    },
    question_practice: {
      sessions: 1,
      correct: 7,
      total: 7,
      accuracy: 100,
      avg_response_time_ms: 3200,
      avg_clarity: 90,
    },
    information_practice: {
      sessions: 1,
      correct: 0,
      total: 0,
      accuracy: 0,
      avg_response_time_sec: 0,
      hint_rate: 0,
    },
  },
  session_history: [],
}

const mockStatus = {
  contact_count: 8,
  item_count: 3,
  total_count: 11,
  can_start_session: true,
  min_contacts_required: 2,
}

function setupProgressMocks(page: import('@playwright/test').Page) {
  return Promise.all([
    // Catch-all first
    page.route('**/api/**', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: '[]' }),
    ),
    page.route('**/api/profile**', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockProfile),
      }),
    ),
    page.route('**/api/life-words/progress**', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockProgress),
      }),
    ),
    page.route('**/api/life-words/status**', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockStatus),
      }),
    ),
    page.route('**/api/stripe/status**', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          account_status: 'active',
          is_paid: true,
          is_trial_active: false,
          can_practice: true,
          has_subscription: true,
          trial_ends_at: null,
        }),
      }),
    ),
  ])
}

test.describe('Progress Page', () => {
  test.beforeEach(async ({ page }) => {
    await mockAuth(page)
    await setupProgressMocks(page)
  })

  test('renders progress page with overall summary', async ({ page }) => {
    await page.goto('/dashboard/practice/progress')

    await expect(page.getByRole('heading', { name: /Your Progress/i })).toBeVisible()
    await expect(page.getByText(/Overall Summary/i)).toBeVisible()
  })

  test('shows total sessions count', async ({ page }) => {
    await page.goto('/dashboard/practice/progress')

    await expect(page.getByText('3', { exact: true })).toBeVisible()
    await expect(page.getByText('Total Sessions')).toBeVisible()
  })

  test('shows overall accuracy', async ({ page }) => {
    await page.goto('/dashboard/practice/progress')

    // 11 correct / 12 total = 92%
    await expect(page.getByText('92%')).toBeVisible()
    await expect(page.getByText('Overall Accuracy')).toBeVisible()
  })

  test('shows all three practice type sections', async ({ page }) => {
    await page.goto('/dashboard/practice/progress')

    await expect(page.getByText('Name Practice')).toBeVisible()
    await expect(page.getByText('Question Practice')).toBeVisible()
    await expect(page.getByText('Information Practice')).toBeVisible()
  })

  test('displays correct and total attempts', async ({ page }) => {
    await page.goto('/dashboard/practice/progress')

    // 4 + 7 + 0 = 11 correct, 5 + 7 + 0 = 12 total
    await expect(page.getByText('11')).toBeVisible()
    await expect(page.getByText('Correct Answers').first()).toBeVisible()
    await expect(page.getByText('12')).toBeVisible()
  })

  test('has back link to Life Words home', async ({ page }) => {
    await page.goto('/dashboard/practice/progress')

    await expect(page.getByText(/Back to Life Words/i)).toBeVisible()
  })
})

test.describe('Preparation Page', () => {
  test.beforeEach(async ({ page }) => {
    await mockAuth(page)
    await setupProgressMocks(page)
  })

  test('renders preparation page with steps', async ({ page }) => {
    await page.goto('/dashboard/practice/preparation')

    await expect(page.getByRole('heading', { name: /Preparation/i })).toBeVisible()
  })

  test('shows step-by-step preparation instructions', async ({ page }) => {
    await page.goto('/dashboard/practice/preparation')

    // Should have numbered phase headings
    await expect(page.getByText(/Getting Started/i)).toBeVisible()
    await expect(page.getByText(/Add Your People/i)).toBeVisible()
  })

  test('has back link to practice home', async ({ page }) => {
    await page.goto('/dashboard/practice/preparation')

    await expect(page.getByText(/Back/i).first()).toBeVisible()
  })
})

test.describe('Progress Page - Mobile', () => {
  test.use({ viewport: { width: 375, height: 812 } })

  test.beforeEach(async ({ page }) => {
    await mockAuth(page)
    await setupProgressMocks(page)
  })

  test('renders correctly on mobile with no horizontal scroll', async ({ page }) => {
    await page.goto('/dashboard/practice/progress')

    await expect(page.getByRole('heading', { name: /Your Progress/i })).toBeVisible()

    const overflows = await page.evaluate(
      () => document.body.scrollWidth > window.innerWidth,
    )
    expect(overflows).toBe(false)
  })

  test('practice sections stack vertically on mobile', async ({ page }) => {
    await page.goto('/dashboard/practice/progress')

    // All sections should be visible
    await expect(page.getByText('Name Practice')).toBeVisible()
    await expect(page.getByText('Question Practice')).toBeVisible()
    await expect(page.getByText('Information Practice')).toBeVisible()
  })
})
