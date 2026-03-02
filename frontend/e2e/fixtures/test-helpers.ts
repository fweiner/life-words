import { Page } from '@playwright/test'

/**
 * Block all backend API calls with empty 200 responses.
 * Must be called BEFORE page.goto().
 */
export async function blockBackendApis(page: Page): Promise<void> {
  await page.route('**/api/**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: '[]',
    }),
  )
}

/**
 * Build the fake session object and JWT for auth mocking.
 */
function buildMockSession() {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
  const now = Math.floor(Date.now() / 1000)
  const payload = btoa(
    JSON.stringify({
      sub: 'e2e-test-user-id',
      email: 'e2e-test@example.com',
      role: 'authenticated',
      aud: 'authenticated',
      exp: now + 3600,
      iat: now,
      user_metadata: {},
      app_metadata: { provider: 'email' },
    }),
  )
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
  const fakeJwt = `${header}.${payload}.e2e-test-signature`

  return {
    access_token: fakeJwt,
    token_type: 'bearer',
    expires_in: 3600,
    expires_at: now + 3600,
    refresh_token: 'e2e-fake-refresh-token',
    user: {
      id: 'e2e-test-user-id',
      aud: 'authenticated',
      role: 'authenticated',
      email: 'e2e-test@example.com',
      email_confirmed_at: '2024-01-01T00:00:00Z',
      user_metadata: {},
      app_metadata: { provider: 'email' },
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
  }
}

/**
 * Mock Supabase authentication for E2E tests.
 *
 * Sets HTTP cookies (via context.addCookies) so the Next.js middleware
 * reads them server-side and passes auth checks via the mock auth server.
 * Also intercepts browser-side Supabase auth API calls.
 *
 * Must be called BEFORE page.goto().
 */
export async function mockAuth(page: Page): Promise<void> {
  const session = buildMockSession()
  const sessionJson = JSON.stringify(session)

  // Set HTTP cookies so the Next.js middleware can read them server-side.
  // Supabase SSR stores sessions as chunked cookies.
  // Key format: sb-{project-ref}-auth-token.{chunk-index}
  // When using the mock server, the project ref comes from the mock URL.
  // The Supabase SSR library derives the storage key from the URL.
  // For http://localhost:54321, the key is: sb-localhost-auth-token
  const storageKey = 'sb-localhost-auth-token'
  const chunks: string[] = []
  for (let i = 0; i < sessionJson.length; i += 3180) {
    chunks.push(sessionJson.slice(i, i + 3180))
  }

  const cookies = chunks.map((chunk, i) => ({
    name: `${storageKey}.${i}`,
    value: encodeURIComponent(chunk),
    domain: 'localhost',
    path: '/',
    expires: Math.floor(Date.now() / 1000) + 3600,
  }))

  await page.context().addCookies(cookies)

  // Also intercept browser-side Supabase auth API calls
  await page.route('**/auth/v1/**', (route) => {
    const url = route.request().url()
    if (url.includes('/token')) {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: sessionJson,
      })
    }
    if (url.includes('/user')) {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(session.user),
      })
    }
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: '{}',
    })
  })
}

/**
 * Mock auth + Life-Words-specific API endpoints for dashboard tests.
 * Mocks the status, sessions, and profile endpoints with realistic data.
 * Must be called BEFORE page.goto().
 */
export async function mockAuthAndApis(page: Page): Promise<void> {
  await mockAuth(page)

  // IMPORTANT: In Playwright, the LAST registered route takes priority.
  // Register the catch-all FIRST, then specific routes override it.

  // Catch-all for any API calls (registered first = lowest priority)
  await page.route('**/api/**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: '[]',
    }),
  )

  // Mock sessions endpoint
  await page.route('**/api/life-words/sessions**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    }),
  )

  // Mock profile endpoint
  await page.route('**/api/profile**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'e2e-test-user-id',
        email: 'e2e-test@example.com',
        first_name: 'Test',
        role: 'patient',
      }),
    }),
  )

  // Mock life-words information-status endpoint
  await page.route('**/api/life-words/information-status**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        can_start_session: true,
        filled_fields_count: 8,
        min_fields_required: 5,
      }),
    }),
  )

  // Mock life-words status endpoint
  await page.route('**/api/life-words/status**', (route) =>
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
  )

  // Mock Stripe subscription status (registered last = highest priority)
  await page.route('**/api/stripe/status**', (route) =>
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
  )
}
