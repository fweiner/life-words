'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase'
import { apiClient } from '@/lib/api/client'
import type { AdminUserStats } from '@/lib/api/types'
import Link from 'next/link'

const ADMIN_EMAIL = 'weiner@parrotsoftware.com'

export default function AdminPage() {
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null)
  const [users, setUsers] = useState<AdminUserStats[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      const supabase = createClient()
      const { data: { user } } = await supabase.auth.getUser()

      if (!user || user.email !== ADMIN_EMAIL) {
        setIsAdmin(false)
        setLoading(false)
        return
      }

      setIsAdmin(true)

      try {
        const data = await apiClient.get<AdminUserStats[]>('/api/admin/users')
        setUsers(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load users')
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [])

  const handleDelete = async (userId: string, email: string) => {
    if (!window.confirm(`Are you sure you want to delete ${email}? This will permanently remove all their data.`)) {
      return
    }

    try {
      await apiClient.delete(`/api/admin/users/${userId}`)
      setUsers(prev => prev.filter(u => u.id !== userId))
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete user')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-xl text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (isAdmin === false) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Access Denied</h1>
        <p className="text-xl text-gray-600 mb-6">You do not have permission to view this page.</p>
        <Link
          href="/dashboard"
          className="text-lg text-[var(--color-primary)] hover:underline font-semibold"
        >
          Return to Dashboard
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Admin: Users</h1>
        <Link
          href="/dashboard"
          className="text-lg text-[var(--color-primary)] hover:underline font-semibold"
        >
          &larr; Dashboard
        </Link>
      </div>

      {error && (
        <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
          <p className="text-red-700 font-semibold">{error}</p>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-lg text-gray-600 mb-4">
          {users.length} registered user{users.length !== 1 ? 's' : ''}
        </p>

        {users.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <p className="text-xl text-gray-600">No users found.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-lg">
              <thead>
                <tr className="border-b-2 border-gray-200">
                  <th className="text-left py-4 px-4 font-bold">Email</th>
                  <th className="text-left py-4 px-4 font-bold">Name</th>
                  <th className="text-left py-4 px-4 font-bold">Signup Date</th>
                  <th className="text-right py-4 px-4 font-bold">Sessions</th>
                  <th className="text-right py-4 px-4 font-bold">Contacts</th>
                  <th className="text-right py-4 px-4 font-bold">Items</th>
                  <th className="text-left py-4 px-4 font-bold">Last Active</th>
                  <th className="text-center py-4 px-4 font-bold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-4 px-4 break-all">{u.email}</td>
                    <td className="py-4 px-4">{u.full_name || '—'}</td>
                    <td className="py-4 px-4 whitespace-nowrap">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-4 px-4 text-right">{u.session_count}</td>
                    <td className="py-4 px-4 text-right">{u.contact_count}</td>
                    <td className="py-4 px-4 text-right">{u.item_count}</td>
                    <td className="py-4 px-4 whitespace-nowrap">
                      {u.last_active_at
                        ? new Date(u.last_active_at).toLocaleDateString()
                        : '—'}
                    </td>
                    <td className="py-4 px-4 text-center">
                      <button
                        onClick={() => handleDelete(u.id, u.email)}
                        className="py-2 px-4 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors text-base"
                        style={{ minHeight: '44px' }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
