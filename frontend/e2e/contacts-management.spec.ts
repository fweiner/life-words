import { test, expect } from '@playwright/test'
import { mockAuth } from './fixtures/test-helpers'

const mockContacts = [
  {
    id: 'contact-1',
    user_id: 'e2e-test-user-id',
    name: 'Ruby Weiner',
    nickname: 'Rubes',
    relationship: 'granddaughter',
    photo_url: 'https://example.com/ruby.jpg',
    pronunciation: '',
    physical_description: 'Young woman with brown hair',
    personality: 'Energetic and fun',
    shared_memories: 'Beach trips together',
    how_you_know: 'Family',
    interests: 'Photography',
    fun_fact: 'Loves sushi',
    created_at: '2024-01-01T00:00:00Z',
    deleted_at: null,
  },
  {
    id: 'contact-2',
    user_id: 'e2e-test-user-id',
    name: 'Charlotte Yanni',
    nickname: 'Charchar',
    relationship: 'granddaughter',
    photo_url: 'https://example.com/charlotte.jpg',
    pronunciation: '',
    physical_description: 'Girl with red hair',
    personality: 'Creative and kind',
    shared_memories: 'Art projects',
    how_you_know: 'Family',
    interests: 'Drawing',
    fun_fact: 'Collects stickers',
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
    // Contacts list
    page.route('**/api/life-words/contacts**', (route) => {
      if (route.request().method() === 'GET') {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockContacts),
        })
      }
      if (route.request().method() === 'POST') {
        return route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({ id: 'new-contact-id', ...mockContacts[0] }),
        })
      }
      return route.continue()
    }),
    // Individual contact
    page.route('**/api/life-words/contacts/*', (route) => {
      if (route.request().method() === 'GET') {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockContacts[0]),
        })
      }
      if (route.request().method() === 'PUT') {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockContacts[0]),
        })
      }
      if (route.request().method() === 'DELETE') {
        return route.fulfill({ status: 200, contentType: 'application/json', body: '{}' })
      }
      return route.continue()
    }),
  ])
}

test.describe('Contacts Management', () => {
  test.beforeEach(async ({ page }) => {
    await mockAuth(page)
    await setupApiMocks(page)
  })

  test('renders contacts list with people cards', async ({ page }) => {
    await page.goto('/dashboard/practice/contacts')

    await expect(page.getByRole('heading', { name: /Manage My People/i })).toBeVisible()
    await expect(page.getByText('2 people saved')).toBeVisible()
    await expect(page.getByText('Ruby Weiner')).toBeVisible()
    await expect(page.getByText('Charlotte Yanni')).toBeVisible()
  })

  test('shows Quick Add Photos, Add with Details, and Invite via Email buttons', async ({
    page,
  }) => {
    await page.goto('/dashboard/practice/contacts')

    await expect(page.getByRole('link', { name: /Quick Add Photos/i })).toBeVisible()
    await expect(page.getByRole('link', { name: /Add with Details/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /Invite via Email/i })).toBeVisible()
  })

  test('displays nickname and relationship for each contact', async ({ page }) => {
    await page.goto('/dashboard/practice/contacts')

    await expect(page.getByText('"Rubes"')).toBeVisible()
    await expect(page.getByText('granddaughter').first()).toBeVisible()
  })

  test('shows edit and remove actions for each contact', async ({ page }) => {
    await page.goto('/dashboard/practice/contacts')

    const editLinks = page.getByRole('link', { name: /Edit/i })
    await expect(editLinks.first()).toBeVisible()

    const removeButtons = page.getByRole('button', { name: /Remove/i })
    await expect(removeButtons.first()).toBeVisible()
  })

  test('has a back link to practice home', async ({ page }) => {
    await page.goto('/dashboard/practice/contacts')

    await expect(page.getByText(/Back/i).first()).toBeVisible()
  })

  test('invite via email button opens modal', async ({ page }) => {
    await page.goto('/dashboard/practice/contacts')

    await page.getByRole('button', { name: /Invite via Email/i }).click()

    await expect(page.getByText(/Send Invite/i)).toBeVisible()
  })
})

test.describe('Contacts Management - Add New Contact', () => {
  test.beforeEach(async ({ page }) => {
    await mockAuth(page)
    await setupApiMocks(page)
  })

  test('add form renders with all required fields', async ({ page }) => {
    await page.goto('/dashboard/practice/contacts/new')

    await expect(page.getByRole('heading', { name: /Add New Contact/i })).toBeVisible()
    await expect(page.getByLabel(/^Name/)).toBeVisible()
    await expect(page.getByLabel(/Nickname/i)).toBeVisible()
    await expect(page.getByLabel(/Relationship/i)).toBeVisible()
  })

  test('shows validation error when submitting empty form', async ({ page }) => {
    await page.goto('/dashboard/practice/contacts/new')

    await page.getByRole('button', { name: /Add Contact/i }).click()

    // Native HTML validation prevents submission — form stays visible
    await expect(page.getByRole('heading', { name: /Add New Contact/i })).toBeVisible()
    // Name field has required attribute
    await expect(page.getByLabel(/^Name/)).toHaveAttribute('required', '')
  })

  test('shows error when photo not uploaded', async ({ page }) => {
    await page.goto('/dashboard/practice/contacts/new')

    // Fill required HTML fields to bypass native validation
    await page.getByLabel(/^Name/).fill('Test Person')
    await page.getByLabel(/Relationship/i).selectOption({ index: 1 })

    await page.getByRole('button', { name: /Add Contact/i }).click()

    await expect(page.getByText(/upload a photo/i)).toBeVisible()
  })
})

test.describe('Contacts Management - Mobile', () => {
  test.use({ viewport: { width: 375, height: 812 } })

  test.beforeEach(async ({ page }) => {
    await mockAuth(page)
    await setupApiMocks(page)
  })

  test('renders correctly on mobile viewport', async ({ page }) => {
    await page.goto('/dashboard/practice/contacts')

    await expect(page.getByRole('heading', { name: /Manage My People/i })).toBeVisible()

    // Verify no horizontal scrollbar
    const overflows = await page.evaluate(
      () => document.body.scrollWidth > window.innerWidth,
    )
    expect(overflows).toBe(false)
  })

  test('buttons stack vertically on mobile', async ({ page }) => {
    await page.goto('/dashboard/practice/contacts')

    // All action buttons should be visible
    await expect(page.getByRole('link', { name: /Quick Add Photos/i })).toBeVisible()
    await expect(page.getByRole('link', { name: /Add with Details/i })).toBeVisible()
    await expect(page.getByRole('button', { name: /Invite via Email/i })).toBeVisible()
  })
})
