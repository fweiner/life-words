'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase'
import { apiClient } from '@/lib/api/client'
import type { AdminUserStats, ErrorLogEntry } from '@/lib/api/types'
import Link from 'next/link'

const ADMIN_EMAIL = 'weiner@parrotsoftware.com'

type Tab = 'users' | 'errors'

function getTrialStatus(user: AdminUserStats): 'paid' | 'trial' | 'expired' {
  if (user.account_status === 'paid') return 'paid'
  if (!user.trial_ends_at) return 'expired'
  return new Date(user.trial_ends_at) > new Date() ? 'trial' : 'expired'
}

function StatusBadge({ user }: { user: AdminUserStats }) {
  const status = getTrialStatus(user)
  if (status === 'paid') {
    return (
      <span className="inline-block px-3 py-1 text-sm font-semibold rounded-full bg-green-100 text-green-800">
        Paid
      </span>
    )
  }
  if (status === 'trial') {
    return (
      <span className="inline-block px-3 py-1 text-sm font-semibold rounded-full bg-yellow-100 text-yellow-800">
        Trial — expires {new Date(user.trial_ends_at!).toLocaleDateString()}
      </span>
    )
  }
  return (
    <span className="inline-block px-3 py-1 text-sm font-semibold rounded-full bg-red-100 text-red-800">
      Trial Expired
    </span>
  )
}

export default function AdminPage() {
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null)
  const [users, setUsers] = useState<AdminUserStats[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<Tab>('users')

  // Error logs state
  const [errorLogs, setErrorLogs] = useState<ErrorLogEntry[]>([])
  const [errorLogsLoading, setErrorLogsLoading] = useState(false)
  const [errorLogsError, setErrorLogsError] = useState<string | null>(null)
  const [expandedLogId, setExpandedLogId] = useState<string | null>(null)

  // Trial date picker state
  const [editingUserId, setEditingUserId] = useState<string | null>(null)
  const [trialDate, setTrialDate] = useState('')

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

  const loadErrorLogs = async () => {
    setErrorLogsLoading(true)
    setErrorLogsError(null)
    try {
      const data = await apiClient.get<ErrorLogEntry[]>('/api/admin/error-logs')
      setErrorLogs(data)
    } catch (err) {
      setErrorLogsError(err instanceof Error ? err.message : 'Failed to load error logs')
    } finally {
      setErrorLogsLoading(false)
    }
  }

  const handleTabChange = (tab: Tab) => {
    setActiveTab(tab)
    if (tab === 'errors' && errorLogs.length === 0 && !errorLogsLoading) {
      loadErrorLogs()
    }
  }

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

  const handleSetPaid = async (userId: string) => {
    try {
      await apiClient.patch(`/api/admin/users/${userId}/account-status`, {
        account_status: 'paid',
      })
      setUsers(prev =>
        prev.map(u =>
          u.id === userId ? { ...u, account_status: 'paid', trial_ends_at: null } : u
        )
      )
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update status')
    }
  }

  const handleSetTrial = async (userId: string) => {
    if (!trialDate) {
      alert('Please select a trial end date')
      return
    }
    try {
      await apiClient.patch(`/api/admin/users/${userId}/account-status`, {
        account_status: 'trial',
        trial_ends_at: new Date(trialDate).toISOString(),
      })
      setUsers(prev =>
        prev.map(u =>
          u.id === userId
            ? { ...u, account_status: 'trial', trial_ends_at: new Date(trialDate).toISOString() }
            : u
        )
      )
      setEditingUserId(null)
      setTrialDate('')
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update status')
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
        <h1 className="text-3xl font-bold text-gray-900">Admin</h1>
        <Link
          href="/dashboard"
          className="text-lg text-[var(--color-primary)] hover:underline font-semibold"
        >
          &larr; Dashboard
        </Link>
      </div>

      {/* Tab navigation */}
      <div className="flex gap-2 border-b border-gray-200">
        <button
          onClick={() => handleTabChange('users')}
          className={`px-5 py-3 text-lg font-semibold border-b-3 transition-colors ${
            activeTab === 'users'
              ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
          style={{ minHeight: '44px' }}
        >
          Users
        </button>
        <button
          onClick={() => handleTabChange('errors')}
          className={`px-5 py-3 text-lg font-semibold border-b-3 transition-colors ${
            activeTab === 'errors'
              ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
          style={{ minHeight: '44px' }}
        >
          Error Logs
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
          <p className="text-red-700 font-semibold">{error}</p>
        </div>
      )}

      {/* Users tab */}
      {activeTab === 'users' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <p className="text-lg text-gray-600 mb-4">
            {users.length} registered user{users.length !== 1 ? 's' : ''}
          </p>

          {users.length === 0 ? (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <p className="text-xl text-gray-600">No users found.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {users.map(u => (
                <div key={u.id} className="border border-gray-200 rounded-lg p-5 hover:bg-gray-50">
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div className="min-w-0">
                      <div className="flex items-center gap-3 flex-wrap mb-1">
                        <p className="text-xl font-semibold text-gray-900 truncate">
                          {u.full_name || 'No name'}
                        </p>
                        <StatusBadge user={u} />
                      </div>
                      <p className="text-lg text-gray-600 break-all">{u.email}</p>
                    </div>
                    <button
                      onClick={() => handleDelete(u.id, u.email)}
                      className="py-2 px-4 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors text-base flex-shrink-0"
                      style={{ minHeight: '44px' }}
                    >
                      Delete
                    </button>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-base">
                    <div>
                      <span className="text-gray-500">Signed up</span>
                      <p className="font-semibold">{new Date(u.created_at).toLocaleDateString()}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Sessions</span>
                      <p className="font-semibold">{u.session_count}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Contacts</span>
                      <p className="font-semibold">{u.contact_count}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Items</span>
                      <p className="font-semibold">{u.item_count}</p>
                    </div>
                  </div>

                  {u.last_active_at && (
                    <p className="text-base text-gray-500 mt-3">
                      Last active: {new Date(u.last_active_at).toLocaleDateString()}
                    </p>
                  )}

                  {/* Account status controls */}
                  <div className="flex items-center gap-3 mt-4 pt-3 border-t border-gray-100 flex-wrap">
                    {u.account_status !== 'paid' && (
                      <button
                        onClick={() => handleSetPaid(u.id)}
                        className="py-2 px-4 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors text-base"
                        style={{ minHeight: '44px' }}
                      >
                        Set Paid
                      </button>
                    )}
                    {editingUserId === u.id ? (
                      <div className="flex items-center gap-2 flex-wrap">
                        <input
                          type="date"
                          value={trialDate}
                          onChange={e => setTrialDate(e.target.value)}
                          className="border border-gray-300 rounded-lg px-3 py-2 text-base"
                          style={{ minHeight: '44px' }}
                          min={new Date().toISOString().split('T')[0]}
                        />
                        <button
                          onClick={() => handleSetTrial(u.id)}
                          className="py-2 px-4 bg-yellow-600 hover:bg-yellow-700 text-white font-semibold rounded-lg transition-colors text-base"
                          style={{ minHeight: '44px' }}
                        >
                          Confirm
                        </button>
                        <button
                          onClick={() => { setEditingUserId(null); setTrialDate('') }}
                          className="py-2 px-4 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold rounded-lg transition-colors text-base"
                          style={{ minHeight: '44px' }}
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => { setEditingUserId(u.id); setTrialDate('') }}
                        className="py-2 px-4 bg-yellow-500 hover:bg-yellow-600 text-white font-semibold rounded-lg transition-colors text-base"
                        style={{ minHeight: '44px' }}
                      >
                        Set Trial
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Error Logs tab */}
      {activeTab === 'errors' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <p className="text-lg text-gray-600">
              {errorLogs.length} error log{errorLogs.length !== 1 ? 's' : ''}
            </p>
            <button
              onClick={loadErrorLogs}
              className="py-2 px-4 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold rounded-lg transition-colors text-base"
              style={{ minHeight: '44px' }}
            >
              Refresh
            </button>
          </div>

          {errorLogsError && (
            <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 mb-4">
              <p className="text-red-700 font-semibold">{errorLogsError}</p>
            </div>
          )}

          {errorLogsLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : errorLogs.length === 0 ? (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <p className="text-xl text-gray-600">No error logs found.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {errorLogs.map(log => (
                <div key={log.id} className="border border-gray-200 rounded-lg p-4">
                  <button
                    onClick={() => setExpandedLogId(expandedLogId === log.id ? null : log.id)}
                    className="w-full text-left"
                    style={{ minHeight: '44px' }}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <div className="flex items-center gap-2 flex-wrap mb-1">
                          <span className="inline-block px-2 py-0.5 text-sm font-mono font-semibold rounded bg-red-100 text-red-800">
                            {log.status_code}
                          </span>
                          <span className="text-base font-semibold text-gray-900">
                            {log.method} {log.endpoint}
                          </span>
                        </div>
                        <p className="text-base text-gray-700 truncate">{log.error_message}</p>
                      </div>
                      <span className="text-sm text-gray-500 flex-shrink-0 whitespace-nowrap">
                        {new Date(log.timestamp).toLocaleString()}
                      </span>
                    </div>
                  </button>

                  {expandedLogId === log.id && (
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <div className="space-y-2">
                        <div>
                          <span className="text-sm text-gray-500">Error message:</span>
                          <p className="text-base text-gray-800">{log.error_message}</p>
                        </div>
                        {log.user_id && (
                          <div>
                            <span className="text-sm text-gray-500">User ID:</span>
                            <p className="text-base text-gray-800 font-mono">{log.user_id}</p>
                          </div>
                        )}
                        {log.traceback && (
                          <div>
                            <span className="text-sm text-gray-500">Traceback:</span>
                            <pre className="mt-1 p-3 bg-gray-900 text-green-400 text-sm rounded-lg overflow-x-auto whitespace-pre-wrap break-words">
                              {log.traceback}
                            </pre>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
