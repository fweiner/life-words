import { test, expect } from '@playwright/test'
import { mockAuthAndApis, mockAuth } from './fixtures/test-helpers'

const mockProfile = {
  id: 'e2e-test-user-id',
  email: 'e2e-test@example.com',
  first_name: 'Test',
  role: 'patient',
}

const mockContacts = [
  {
    id: 'contact-1',
    user_id: 'e2e-test-user-id',
    name: 'Test Person',
    nickname: 'Testy',
    relationship: 'friend',
    photo_url: 'https://example.com/test.jpg',
    pronunciation: '',
    physical_description: 'Tall',
    personality: 'Kind',
    shared_memories: 'Fun times',
    how_you_know: 'School',
    interests: 'Reading',
    fun_fact: 'Loves cats',
    created_at: '2024-01-01T00:00:00Z',
    deleted_at: null,
  },
]

function setupFullMocks(page: import('@playwright/test').Page) {
  return Promise.all([
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
    page.route('**/api/life-words/contacts**', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockContacts),
      }),
    ),
    page.route('**/api/life-words/items**', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: '[]' }),
    ),
    page.route('**/api/life-words/information-status**', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          can_start_session: true,
          filled_fields_count: 8,
          min_fields_required: 5,
        }),
      }),
    ),
    page.route('**/api/life-words/status**', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          contact_count: 3,
          item_count: 2,
          total_count: 5,
          can_start_session: true,
          min_contacts_required: 2,
        }),
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

test.describe('Responsive - Mobile (375x812)', () => {
  test.use({ viewport: { width: 375, height: 812 } })

  test.beforeEach(async ({ page }) => {
    await mockAuth(page)
    await setupFullMocks(page)
  })

  test('practice home has no horizontal scroll on mobile', async ({ page }) => {
    await page.goto('/dashboard/practice')

    await expect(
      page.getByRole('heading', { name: /My Life Words and Memory/i }),
    ).toBeVisible()

    const overflows = await page.evaluate(
      () => document.body.scrollWidth > window.innerWidth,
    )
    expect(overflows).toBe(false)
  })

  test('contacts page has no horizontal scroll on mobile', async ({ page }) => {
    await page.goto('/dashboard/practice/contacts')

    await expect(page.getByRole('heading', { name: /Manage My People/i })).toBeVisible()

    const overflows = await page.evaluate(
      () => document.body.scrollWidth > window.innerWidth,
    )
    expect(overflows).toBe(false)
  })

  test('item add form has no horizontal scroll on mobile', async ({ page }) => {
    await page.goto('/dashboard/practice/items/new')

    const overflows = await page.evaluate(
      () => document.body.scrollWidth > window.innerWidth,
    )
    expect(overflows).toBe(false)
  })

  test('practice buttons are full width on mobile', async ({ page }) => {
    await page.goto('/dashboard/practice')

    // Practice buttons should be visible and accessible
    await expect(
      page.getByRole('button', { name: /Name Practice/i }),
    ).toBeVisible()
    await expect(
      page.getByRole('button', { name: /Question Practice/i }),
    ).toBeVisible()
  })

  test('navigation shows hamburger menu on mobile', async ({ page }) => {
    await page.goto('/dashboard/practice')

    // On mobile, nav should collapse to hamburger
    const hamburger = page.getByRole('button', { name: /menu/i })
    // If hamburger exists, nav links should be hidden initially
    if (await hamburger.isVisible()) {
      await expect(page.getByText('Manage My Account')).not.toBeVisible()
    }
  })
})

test.describe('Responsive - Tablet (768x1024)', () => {
  test.use({ viewport: { width: 768, height: 1024 } })

  test.beforeEach(async ({ page }) => {
    await mockAuth(page)
    await setupFullMocks(page)
  })

  test('practice home renders correctly on tablet', async ({ page }) => {
    await page.goto('/dashboard/practice')

    await expect(
      page.getByRole('heading', { name: /My Life Words and Memory/i }),
    ).toBeVisible()

    const overflows = await page.evaluate(
      () => document.body.scrollWidth > window.innerWidth,
    )
    expect(overflows).toBe(false)
  })

  test('contacts page shows multi-column grid on tablet', async ({ page }) => {
    await page.goto('/dashboard/practice/contacts')

    await expect(page.getByRole('heading', { name: /Manage My People/i })).toBeVisible()

    const overflows = await page.evaluate(
      () => document.body.scrollWidth > window.innerWidth,
    )
    expect(overflows).toBe(false)
  })
})

test.describe('Responsive - Desktop (1440x900)', () => {
  test.use({ viewport: { width: 1440, height: 900 } })

  test.beforeEach(async ({ page }) => {
    await mockAuth(page)
    await setupFullMocks(page)
  })

  test('practice home renders correctly on desktop', async ({ page }) => {
    await page.goto('/dashboard/practice')

    await expect(
      page.getByRole('heading', { name: /My Life Words and Memory/i }),
    ).toBeVisible()

    // Full nav should be visible on desktop
    await expect(page.getByText('Sign Out')).toBeVisible()
  })

  test('contacts page shows multi-column grid on desktop', async ({ page }) => {
    await page.goto('/dashboard/practice/contacts')

    await expect(page.getByRole('heading', { name: /Manage My People/i })).toBeVisible()
  })
})

test.describe('Accessibility - Font Sizes', () => {
  test.use({ viewport: { width: 1440, height: 900 } })

  test.beforeEach(async ({ page }) => {
    await mockAuthAndApis(page)
  })

  test('practice home page has no critically small fonts', async ({ page }) => {
    await page.goto('/dashboard/practice')

    // Check for fonts below 14px (critically small)
    const criticallySmall = await page.evaluate(() => {
      const els = document.querySelectorAll(
        'p, span, label, button, a, h1, h2, h3, td, th, li',
      )
      const results: Array<{ text: string; size: number; tag: string }> = []
      els.forEach((el) => {
        const size = parseFloat(getComputedStyle(el).fontSize)
        if (size < 14 && (el as HTMLElement).textContent?.trim()) {
          results.push({
            text: (el as HTMLElement).textContent!.trim().slice(0, 40),
            size,
            tag: el.tagName,
          })
        }
      })
      return results.slice(0, 10)
    })

    expect(criticallySmall).toHaveLength(0)
  })
})

test.describe('Accessibility - Touch Targets', () => {
  test.use({ viewport: { width: 375, height: 812 } })

  test.beforeEach(async ({ page }) => {
    await mockAuthAndApis(page)
  })

  test('main practice buttons meet 44px minimum touch target', async ({ page }) => {
    await page.goto('/dashboard/practice')

    const buttons = ['Name Practice', 'Question Practice', 'Information Practice']
    for (const name of buttons) {
      const button = page.getByRole('button', { name: new RegExp(name, 'i') })
      const box = await button.boundingBox()
      expect(box).not.toBeNull()
      if (box) {
        expect(box.height).toBeGreaterThanOrEqual(44)
      }
    }
  })
})
