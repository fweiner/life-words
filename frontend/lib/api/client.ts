/**
 * Centralized API client for all backend calls.
 *
 * Usage:
 *   import { apiClient } from '@/lib/api/client'
 *   const data = await apiClient.get('/api/profile')
 *   const result = await apiClient.post('/api/matching/evaluate/name', { ... })
 */
import { createClient } from '@/lib/supabase'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export class ApiError extends Error {
  status: number
  detail: string

  constructor(status: number, detail: string) {
    super(detail)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

export async function getAuthToken(): Promise<string | null> {
  try {
    const supabase = createClient()

    // Fast path: session is already hydrated
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.access_token) {
      return session.access_token
    }

    // Fallback: session not yet hydrated — force server-side verification
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) return null

    // getUser() succeeded, so the session should now be available
    const { data: { session: refreshedSession } } = await supabase.auth.getSession()
    return refreshedSession?.access_token ?? null
  } catch {
    return null
  }
}

async function buildHeaders(authenticated: boolean): Promise<Record<string, string>> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (authenticated) {
    const token = await getAuthToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
  }
  return headers
}

async function apiFetch(url: string, init?: RequestInit): Promise<Response> {
  try {
    return await fetch(url, init)
  } catch {
    throw new ApiError(0, 'Unable to connect to the server. Is the backend running?')
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail = `HTTP ${response.status}`
    try {
      const body = await response.json()
      detail = body.detail || body.message || detail
    } catch {
      // response body wasn't JSON
    }
    throw new ApiError(response.status, detail)
  }
  return response.json() as Promise<T>
}

export const apiClient = {
  /**
   * GET request (authenticated by default).
   */
  async get<T = unknown>(path: string, authenticated = true): Promise<T> {
    const headers = await buildHeaders(authenticated)
    const response = await apiFetch(`${API_URL}${path}`, { headers })
    return handleResponse<T>(response)
  },

  /**
   * POST request with JSON body.
   */
  async post<T = unknown>(path: string, body?: unknown, authenticated = true): Promise<T> {
    const headers = await buildHeaders(authenticated)
    const response = await apiFetch(`${API_URL}${path}`, {
      method: 'POST',
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
    return handleResponse<T>(response)
  },

  /**
   * PUT request with JSON body.
   */
  async put<T = unknown>(path: string, body?: unknown, authenticated = true): Promise<T> {
    const headers = await buildHeaders(authenticated)
    const response = await apiFetch(`${API_URL}${path}`, {
      method: 'PUT',
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
    return handleResponse<T>(response)
  },

  /**
   * PATCH request with JSON body.
   */
  async patch<T = unknown>(path: string, body?: unknown, authenticated = true): Promise<T> {
    const headers = await buildHeaders(authenticated)
    const response = await apiFetch(`${API_URL}${path}`, {
      method: 'PATCH',
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
    return handleResponse<T>(response)
  },

  /**
   * DELETE request.
   */
  async delete<T = unknown>(path: string, authenticated = true): Promise<T> {
    const headers = await buildHeaders(authenticated)
    const response = await apiFetch(`${API_URL}${path}`, {
      method: 'DELETE',
      headers,
    })
    return handleResponse<T>(response)
  },

  /**
   * POST with FormData (for file uploads). Does NOT set Content-Type
   * (browser sets multipart boundary automatically).
   */
  async postFormData<T = unknown>(path: string, formData: FormData, authenticated = true): Promise<T> {
    const headers: Record<string, string> = {}
    if (authenticated) {
      const token = await getAuthToken()
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
    }
    const response = await apiFetch(`${API_URL}${path}`, {
      method: 'POST',
      headers,
      body: formData,
    })
    return handleResponse<T>(response)
  },

  /**
   * POST with no auth (public endpoints).
   */
  async postPublic<T = unknown>(path: string, body?: unknown): Promise<T> {
    return this.post<T>(path, body, false)
  },

  /**
   * GET with no auth (public endpoints).
   */
  async getPublic<T = unknown>(path: string): Promise<T> {
    return this.get<T>(path, false)
  },
}
