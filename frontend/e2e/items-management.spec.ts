import { test, expect } from '@playwright/test'
import { mockAuth } from './fixtures/test-helpers'

const mockItems = [
  {
    id: 'item-1',
    user_id: 'e2e-test-user-id',
    name: 'Printer',
    pronunciation: '',
    photo_url: 'https://example.com/printer.jpg',
    purpose: 'Print documents',
    features: 'Wireless, color printing',
    category: 'electronics',
    size: 'Medium',
    shape: 'Rectangular',
    color: 'White',
    weight: 'Medium',
    location: 'Office desk',
    associated_with: 'Work tasks',
    created_at: '2024-01-01T00:00:00Z',
    deleted_at: null,
  },
  {
    id: 'item-2',
    user_id: 'e2e-test-user-id',
    name: 'Laptop',
    pronunciation: '',
    photo_url: 'https://example.com/laptop.jpg',
    purpose: 'Programming',
    features: 'Fast processor, large screen',
    category: 'electronics',
    size: 'Medium',
    shape: 'Rectangular',
    color: 'Silver',
    weight: 'Light',
    location: 'Office',
    associated_with: 'Daily work',
    created_at: '2024-01-02T00:00:00Z',
    deleted_at: null,
  },
]

const mockProfile = {
  id: 'e2e-test-user-id',
  email: 'e2e-test@example.com',
  first_name: 'Test',
  role: 'patient',
}

function setupApiMocks(page: import('@playwright/test').Page) {
  return Promise.all([
    // Catch-all first (lowest priority)
    page.route('**/api/**', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: '[]' }),
    ),
    // Profile
    page.route('**/api/profile**', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockProfile),
      }),
    ),
    // Items list
    page.route('**/api/life-words/items**', (route) => {
      if (route.request().method() === 'GET') {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockItems),
        })
      }
      if (route.request().method() === 'POST') {
        return route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({ id: 'new-item-id', ...mockItems[0] }),
        })
      }
      return route.continue()
    }),
    // Individual item
    page.route('**/api/life-words/items/*', (route) => {
      if (route.request().method() === 'GET') {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockItems[0]),
        })
      }
      if (route.request().method() === 'PUT') {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockItems[0]),
        })
      }
      if (route.request().method() === 'DELETE') {
        return route.fulfill({ status: 200, contentType: 'application/json', body: '{}' })
      }
      return route.continue()
    }),
  ])
}

test.describe('Items Management', () => {
  test.beforeEach(async ({ page }) => {
    await mockAuth(page)
    await setupApiMocks(page)
  })

  test('renders items list with item cards', async ({ page }) => {
    await page.goto('/dashboard/practice/items')

    await expect(page.getByRole('heading', { name: /My Stuff/i })).toBeVisible()
    await expect(page.getByText('2 items saved')).toBeVisible()
    await expect(page.getByText('Printer')).toBeVisible()
    await expect(page.getByText('Laptop')).toBeVisible()
  })

  test('shows Quick Add Photos and Add with Details buttons', async ({ page }) => {
    await page.goto('/dashboard/practice/items')

    await expect(page.getByRole('link', { name: /Quick Add Photos/i })).toBeVisible()
    await expect(page.getByRole('link', { name: /Add with Details/i })).toBeVisible()
  })

  test('displays purpose description for each item', async ({ page }) => {
    await page.goto('/dashboard/practice/items')

    await expect(page.getByText('Print documents')).toBeVisible()
    await expect(page.getByText('Programming')).toBeVisible()
  })

  test('shows edit and remove actions for each item', async ({ page }) => {
    await page.goto('/dashboard/practice/items')

    const editLinks = page.getByRole('link', { name: /Edit/i })
    await expect(editLinks.first()).toBeVisible()

    const removeButtons = page.getByRole('button', { name: /Remove/i })
    await expect(removeButtons.first()).toBeVisible()
  })

  test('has a back link to practice home', async ({ page }) => {
    await page.goto('/dashboard/practice/items')

    await expect(page.getByText(/Back/i).first()).toBeVisible()
  })
})

test.describe('Items Management - Add New Item', () => {
  test.beforeEach(async ({ page }) => {
    await mockAuth(page)
    await setupApiMocks(page)
  })

  test('add form renders with all fields', async ({ page }) => {
    await page.goto('/dashboard/practice/items/new')

    await expect(page.getByRole('heading', { name: /Add New Item/i })).toBeVisible()
    await expect(page.getByLabel(/^Name/)).toBeVisible()
    await expect(page.getByLabel(/Category/i)).toBeVisible()
    await expect(page.getByLabel(/Purpose/i)).toBeVisible()
    await expect(page.getByLabel(/Features/i)).toBeVisible()
    await expect(page.getByLabel(/Size/i)).toBeVisible()
    await expect(page.getByLabel(/Shape/i)).toBeVisible()
    await expect(page.getByLabel(/Color/i)).toBeVisible()
    await expect(page.getByLabel(/Weight/i)).toBeVisible()
    await expect(page.getByLabel(/Location/i)).toBeVisible()
    await expect(page.getByLabel(/Associated With/i)).toBeVisible()
  })

  test('shows validation error when submitting without name', async ({ page }) => {
    await page.goto('/dashboard/practice/items/new')

    await page.getByRole('button', { name: /Add Item/i }).click()

    // Native HTML validation prevents submission — form stays visible
    await expect(page.getByRole('heading', { name: /Add New Item/i })).toBeVisible()
    // Name field has required attribute
    await expect(page.getByLabel(/^Name/)).toHaveAttribute('required', '')
  })

  test('shows minimum description fields notice', async ({ page }) => {
    await page.goto('/dashboard/practice/items/new')

    await expect(
      page.getByText(/fill in at least 6 of the description fields/i),
    ).toBeVisible()
  })

  test('photo upload tip shows item-specific text', async ({ page }) => {
    await page.goto('/dashboard/practice/items/new')

    await expect(
      page.getByText(/Use a clear, well-lit photo of the item/i),
    ).toBeVisible()
  })
})

test.describe('Items Management - Mobile', () => {
  test.use({ viewport: { width: 375, height: 812 } })

  test.beforeEach(async ({ page }) => {
    await mockAuth(page)
    await setupApiMocks(page)
  })

  test('renders correctly on mobile viewport', async ({ page }) => {
    await page.goto('/dashboard/practice/items')

    await expect(page.getByRole('heading', { name: /My Stuff/i })).toBeVisible()

    // Verify no horizontal scrollbar
    const overflows = await page.evaluate(
      () => document.body.scrollWidth > window.innerWidth,
    )
    expect(overflows).toBe(false)
  })
})
