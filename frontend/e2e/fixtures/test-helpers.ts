import { Page } from '@playwright/test';

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
  );
}

/**
 * Mock Supabase authentication for E2E tests.
 * Sets up fake JWT cookie and intercepts Supabase auth API calls.
 * Must be called BEFORE page.goto().
 */
export async function mockAuth(page: Page): Promise<void> {
  // Build a fake JWT with future expiry
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');
  const now = Math.floor(Date.now() / 1000);
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
    .replace(/\//g, '_');
  const fakeJwt = `${header}.${payload}.e2e-test-signature`;

  const session = {
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
  };

  const sessionJson = JSON.stringify(session);

  // Seed the Supabase session cookie in the correct chunked format
  // Life-Words Supabase project ID: nnvqtxwobvyitqbsdskc
  const storageKey = 'sb-nnvqtxwobvyitqbsdskc-auth-token';
  await page.addInitScript(
    (args: { key: string; session: string }) => {
      // Split into chunks of 3180 chars (Supabase SSR default)
      const chunks: string[] = [];
      for (let i = 0; i < args.session.length; i += 3180) {
        chunks.push(args.session.slice(i, i + 3180));
      }
      chunks.forEach((chunk, i) => {
        document.cookie = `${args.key}.${i}=${encodeURIComponent(chunk)}; path=/; max-age=3600`;
      });
    },
    { key: storageKey, session: sessionJson },
  );

  // Intercept Supabase auth API calls
  await page.route('**/auth/v1/**', (route) => {
    const url = route.request().url();
    if (url.includes('/token')) {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: sessionJson,
      });
    }
    if (url.includes('/user')) {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(session.user),
      });
    }
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: '{}',
    });
  });
}

/**
 * Mock auth + Life-Words-specific API endpoints for dashboard tests.
 * Mocks the status, sessions, and profile endpoints with realistic data.
 * Must be called BEFORE page.goto().
 */
export async function mockAuthAndApis(page: Page): Promise<void> {
  await mockAuth(page);

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
  );

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
  );

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
  );

  // Mock sessions endpoint
  await page.route('**/api/life-words/sessions**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    }),
  );

  // Catch-all for any other API calls
  await page.route('**/api/**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: '[]',
    }),
  );
}
