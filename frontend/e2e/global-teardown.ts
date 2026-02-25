import http from 'http'

export default async function globalTeardown() {
  const server = (globalThis as Record<string, unknown>).__mockAuthServer as http.Server | undefined
  if (server) {
    await new Promise<void>((resolve) => server.close(() => resolve()))
    console.log('Mock Supabase auth server stopped')
  }
}
