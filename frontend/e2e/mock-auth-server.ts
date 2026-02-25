/**
 * A minimal mock Supabase auth server for E2E tests.
 * Responds to /auth/v1/user with a mock user when a Bearer token is present.
 * This is needed because Next.js middleware calls supabase.auth.getUser()
 * server-side, which Playwright cannot intercept.
 */
import http from 'http'

export const MOCK_AUTH_PORT = 54321
export const MOCK_SUPABASE_URL = `http://localhost:${MOCK_AUTH_PORT}`

export const mockUser = {
  id: 'e2e-test-user-id',
  aud: 'authenticated',
  role: 'authenticated',
  email: 'e2e-test@example.com',
  email_confirmed_at: '2024-01-01T00:00:00Z',
  user_metadata: {},
  app_metadata: { provider: 'email' },
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

export function createMockAuthServer(): http.Server {
  return http.createServer((req, res) => {
    // CORS headers for browser-side requests
    res.setHeader('Access-Control-Allow-Origin', '*')
    res.setHeader('Access-Control-Allow-Headers', '*')
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    res.setHeader('Content-Type', 'application/json')

    if (req.method === 'OPTIONS') {
      res.writeHead(200)
      res.end()
      return
    }

    const auth = req.headers['authorization']

    // GET /auth/v1/user — verify token and return user
    if (req.url?.includes('/auth/v1/user') && auth?.startsWith('Bearer ')) {
      res.writeHead(200)
      res.end(JSON.stringify(mockUser))
      return
    }

    // POST /auth/v1/token — token refresh
    if (req.url?.includes('/auth/v1/token')) {
      const now = Math.floor(Date.now() / 1000)
      res.writeHead(200)
      res.end(
        JSON.stringify({
          access_token: 'e2e-mock-access-token',
          token_type: 'bearer',
          expires_in: 3600,
          expires_at: now + 3600,
          refresh_token: 'e2e-mock-refresh-token',
          user: mockUser,
        }),
      )
      return
    }

    // Default: 401 for anything else without auth
    res.writeHead(401)
    res.end(JSON.stringify({ error: 'not authenticated' }))
  })
}
