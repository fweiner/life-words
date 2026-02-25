import { createMockAuthServer, MOCK_AUTH_PORT } from './mock-auth-server'

export default async function globalSetup() {
  const server = createMockAuthServer()
  await new Promise<void>((resolve) => server.listen(MOCK_AUTH_PORT, resolve))
  console.log(`Mock Supabase auth server started on port ${MOCK_AUTH_PORT}`)
  ;(globalThis as Record<string, unknown>).__mockAuthServer = server
}
