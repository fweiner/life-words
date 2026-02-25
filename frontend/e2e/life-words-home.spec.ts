import { test, expect } from '@playwright/test'
import { mockAuthAndApis } from './fixtures/test-helpers'

test.describe('Life Words Home Page', () => {
  test.beforeEach(async ({ page }) => {
    await mockAuthAndApis(page)
  })

  test('renders the page with Ready to Practice heading', async ({ page }) => {
    await page.goto('/dashboard/treatments/life-words')

    await expect(
      page.getByRole('heading', { name: /My Life Words and Memory/i }),
    ).toBeVisible()

    await expect(
      page.getByRole('heading', { name: /Ready to Practice/i }),
    ).toBeVisible()

    await expect(
      page.getByText(/3 people and 2 items ready/i),
    ).toBeVisible()
  })

  test('shows Name Practice, Question Practice, and Information Practice buttons', async ({
    page,
  }) => {
    await page.goto('/dashboard/treatments/life-words')

    await expect(
      page.getByRole('button', { name: /Name Practice/i }),
    ).toBeVisible()

    await expect(
      page.getByRole('button', { name: /Question Practice/i }),
    ).toBeVisible()

    await expect(
      page.getByRole('button', { name: /Information Practice/i }),
    ).toBeVisible()
  })

  test('clicking Name Practice shows category selection dialog', async ({
    page,
  }) => {
    await page.goto('/dashboard/treatments/life-words')

    await page.getByRole('button', { name: /Name Practice/i }).click()

    // Category dialog should appear since both people and items exist
    await expect(
      page.getByText(/What would you like to practice/i),
    ).toBeVisible()

    await expect(
      page.getByRole('button', { name: /People \(3\)/i }),
    ).toBeVisible()

    await expect(
      page.getByRole('button', { name: /Stuff \(2\)/i }),
    ).toBeVisible()
  })

  test('shows secondary action links', async ({ page }) => {
    await page.goto('/dashboard/treatments/life-words')

    await expect(page.getByText('Quick Add')).toBeVisible()
    await expect(page.getByText('Instructions')).toBeVisible()
    await expect(page.getByText('Progress')).toBeVisible()
    await expect(page.getByText('My People')).toBeVisible()
    await expect(page.getByText('My Info')).toBeVisible()
    await expect(page.getByText('My Stuff')).toBeVisible()
    await expect(page.getByText('Settings')).toBeVisible()
  })

  test('has a back to dashboard link', async ({ page }) => {
    await page.goto('/dashboard/treatments/life-words')

    const backLink = page.getByText(/Back to Dashboard/i)
    await expect(backLink).toBeVisible()
  })
})

test.describe('Life Words Home Page - Mobile', () => {
  test.use({ viewport: { width: 375, height: 667 } })

  test.beforeEach(async ({ page }) => {
    await mockAuthAndApis(page)
  })

  test('renders correctly on mobile viewport', async ({ page }) => {
    await page.goto('/dashboard/treatments/life-words')

    await expect(
      page.getByRole('heading', { name: /My Life Words and Memory/i }),
    ).toBeVisible()

    await expect(
      page.getByRole('button', { name: /Name Practice/i }),
    ).toBeVisible()

    // Verify no horizontal scrollbar
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth)
    const viewportWidth = await page.evaluate(() => window.innerWidth)
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth)
  })
})
