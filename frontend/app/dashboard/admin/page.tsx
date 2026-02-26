'use client'

import { useEffect, useState, useCallback, useMemo } from 'react'
import { createClient } from '@/lib/supabase'
import { apiClient } from '@/lib/api/client'
import type {
  AdminUserStats,
  AdminCreateUserRequest,
  AdminCreateUserResponse,
  AdminUpdateUserRequest,
  AdminUpdateUserResponse,
  AdminToggleUserResponse,
  ErrorLogEntry,
  ErrorLogListResponse,
} from '@/lib/api/types'
import Link from 'next/link'

const ADMIN_EMAIL = 'weiner@parrotsoftware.com'

type Tab = 'users' | 'errors'

type StatusColor = {
  bg: string
  text: string
  label: string
}

const STATUS_COLORS: Record<string, StatusColor> = {
  paid: { bg: 'bg-green-100', text: 'text-green-800', label: 'Active' },
  trial: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Trial' },
  expired: { bg: 'bg-orange-100', text: 'text-orange-800', label: 'Expired' },
  admin_disabled: { bg: 'bg-red-100', text: 'text-red-800', label: 'Disabled' },
  cancelled: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Canceled' },
  past_due: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Past Due' },
}

function getDisplayStatus(user: AdminUserStats): string {
  if (user.account_status === 'admin_disabled') return 'admin_disabled'
  if (user.account_status === 'paid') return 'paid'
  if (user.account_status === 'cancelled') return 'cancelled'
  if (user.account_status === 'past_due') return 'past_due'
  if (user.account_status === 'trial') {
    if (!user.trial_ends_at) return 'expired'
    return new Date(user.trial_ends_at) > new Date() ? 'trial' : 'expired'
  }
  return user.account_status
}

function StatusBadge({ user }: { user: AdminUserStats }) {
  const status = getDisplayStatus(user)
  const colors = STATUS_COLORS[status] || { bg: 'bg-gray-100', text: 'text-gray-800', label: status }

  let extra = ''
  if (status === 'trial' && user.trial_ends_at) {
    extra = ` — expires ${new Date(user.trial_ends_at).toLocaleDateString()}`
  }

  return (
    <span className={`inline-block px-3 py-1 text-sm font-semibold rounded-full ${colors.bg} ${colors.text}`}>
      {colors.label}{extra}
    </span>
  )
}

function Modal({ open, onClose, title, children }: {
  open: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
}) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-5 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none p-1"
            style={{ minWidth: '44px', minHeight: '44px' }}
          >
            &times;
          </button>
        </div>
        <div className="p-5">{children}</div>
      </div>
    </div>
  )
}

export default function AdminPage() {
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null)
  const [users, setUsers] = useState<AdminUserStats[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<Tab>('users')

  // Search
  const [searchQuery, setSearchQuery] = useState('')

  // Create modal
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [createForm, setCreateForm] = useState<AdminCreateUserRequest>({
    email: '',
    password: '',
    full_name: '',
    account_status: 'trial',
    trial_days: 14,
  })
  const [creating, setCreating] = useState(false)

  // Edit modal
  const [editUser, setEditUser] = useState<AdminUserStats | null>(null)
  const [editForm, setEditForm] = useState<AdminUpdateUserRequest>({})
  const [editing, setEditing] = useState(false)

  // Error logs state
  const [errorLogs, setErrorLogs] = useState<ErrorLogEntry[]>([])
  const [errorLogsTotal, setErrorLogsTotal] = useState(0)
  const [errorLogsPage, setErrorLogsPage] = useState(1)
  const [errorLogsLoading, setErrorLogsLoading] = useState(false)
  const [errorLogsError, setErrorLogsError] = useState<string | null>(null)
  const [expandedLogId, setExpandedLogId] = useState<string | null>(null)
  const [errorSearch, setErrorSearch] = useState('')
  const [errorSourceFilter, setErrorSourceFilter] = useState('')
  const [showResolved, setShowResolved] = useState(false)
  const [resolveNotes, setResolveNotes] = useState('')
  const [resolving, setResolving] = useState(false)

  const perPage = 50

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

  // Client-side filter
  const filteredUsers = useMemo(() => {
    if (!searchQuery.trim()) return users
    const q = searchQuery.toLowerCase()
    return users.filter(u =>
      u.email.toLowerCase().includes(q) ||
      (u.full_name && u.full_name.toLowerCase().includes(q))
    )
  }, [users, searchQuery])

  const loadErrorLogs = useCallback(async (page = 1) => {
    setErrorLogsLoading(true)
    setErrorLogsError(null)
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: perPage.toString(),
      })
      if (errorSearch) params.set('search', errorSearch)
      if (errorSourceFilter) params.set('source', errorSourceFilter)
      if (!showResolved) params.set('resolved', 'false')

      const data = await apiClient.get<ErrorLogListResponse>(`/api/admin/errors?${params}`)
      setErrorLogs(data.errors || [])
      setErrorLogsTotal(data.total || 0)
      setErrorLogsPage(page)
    } catch (err) {
      setErrorLogsError(err instanceof Error ? err.message : 'Failed to load error logs')
    } finally {
      setErrorLogsLoading(false)
    }
  }, [errorSearch, errorSourceFilter, showResolved])

  const handleTabChange = (tab: Tab) => {
    setActiveTab(tab)
    if (tab === 'errors' && errorLogs.length === 0 && !errorLogsLoading) {
      loadErrorLogs()
    }
  }

  // --- User CRUD ---

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreating(true)
    try {
      await apiClient.post<AdminCreateUserResponse>('/api/admin/users', createForm)
      // Refresh user list
      const data = await apiClient.get<AdminUserStats[]>('/api/admin/users')
      setUsers(data)
      setShowCreateModal(false)
      setCreateForm({ email: '', password: '', full_name: '', account_status: 'trial', trial_days: 14 })
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create user')
    } finally {
      setCreating(false)
    }
  }

  const openEditModal = (user: AdminUserStats) => {
    setEditUser(user)
    setEditForm({
      email: user.email,
      full_name: user.full_name || '',
      account_status: user.account_status,
      subscription_plan: user.subscription_plan || '',
      trial_ends_at: user.trial_ends_at ? user.trial_ends_at.split('T')[0] : '',
    })
  }

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editUser) return
    setEditing(true)
    try {
      // Build update payload — only include changed fields
      const payload: AdminUpdateUserRequest = {}
      if (editForm.email && editForm.email !== editUser.email) payload.email = editForm.email
      if (editForm.password) payload.password = editForm.password
      if (editForm.full_name !== undefined && editForm.full_name !== (editUser.full_name || '')) payload.full_name = editForm.full_name
      if (editForm.account_status && editForm.account_status !== editUser.account_status) payload.account_status = editForm.account_status
      if (editForm.subscription_plan !== undefined) payload.subscription_plan = editForm.subscription_plan || undefined
      if (editForm.trial_ends_at) payload.trial_ends_at = new Date(editForm.trial_ends_at).toISOString()

      const result = await apiClient.put<AdminUpdateUserResponse>(`/api/admin/users/${editUser.id}`, payload)
      setUsers(prev => prev.map(u => u.id === editUser.id ? result.user : u))
      setEditUser(null)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update user')
    } finally {
      setEditing(false)
    }
  }

  const handleToggle = async (user: AdminUserStats) => {
    const action = user.account_status === 'admin_disabled' ? 'enable' : 'disable'
    if (!window.confirm(`Are you sure you want to ${action} ${user.email}?`)) return

    try {
      const result = await apiClient.post<AdminToggleUserResponse>(`/api/admin/users/${user.id}/toggle`)
      setUsers(prev => prev.map(u =>
        u.id === user.id ? { ...u, account_status: result.new_status } : u
      ))
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to toggle user')
    }
  }

  const handleDelete = async (userId: string, email: string) => {
    if (!window.confirm(`Are you sure you want to delete ${email}? This will permanently remove all their data.`)) return

    try {
      await apiClient.delete(`/api/admin/users/${userId}`)
      setUsers(prev => prev.filter(u => u.id !== userId))
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete user')
    }
  }

  // --- CSV Export ---

  const exportCSV = () => {
    const headers = ['Email', 'Name', 'Status', 'Plan', 'Signed Up', 'Last Active', 'Sessions', 'Contacts', 'Items', 'Trial Ends', 'Renewal Date']
    const rows = filteredUsers.map(u => [
      u.email,
      u.full_name || '',
      u.account_status,
      u.subscription_plan || '',
      new Date(u.created_at).toLocaleDateString(),
      u.last_active_at ? new Date(u.last_active_at).toLocaleDateString() : '',
      u.session_count.toString(),
      u.contact_count.toString(),
      u.item_count.toString(),
      u.trial_ends_at ? new Date(u.trial_ends_at).toLocaleDateString() : '',
      u.subscription_current_period_end ? new Date(u.subscription_current_period_end).toLocaleDateString() : '',
    ])

    const csv = [headers, ...rows].map(row =>
      row.map(cell => `"${cell.replace(/"/g, '""')}"`).join(',')
    ).join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `users-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  // --- Error log handlers ---

  const handleErrorSearch = (e: React.FormEvent) => {
    e.preventDefault()
    loadErrorLogs(1)
  }

  const handleResolve = async (id: string) => {
    setResolving(true)
    try {
      await apiClient.post(`/api/admin/errors/${id}/resolve`, { notes: resolveNotes || null })
      setResolveNotes('')
      loadErrorLogs(errorLogsPage)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to resolve error')
    } finally {
      setResolving(false)
    }
  }

  const handleUnresolve = async (id: string) => {
    try {
      await apiClient.post(`/api/admin/errors/${id}/unresolve`, {})
      loadErrorLogs(errorLogsPage)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to unresolve error')
    }
  }

  const copyForAI = (err: ErrorLogEntry) => {
    const text = `## Error Log #${err.id}
- **Time:** ${new Date(err.created_at).toLocaleString()}
- **Source:** ${err.source}
- **Endpoint:** ${err.http_method} ${err.endpoint}
- **Status:** ${err.status_code}
- **Type:** ${err.error_type}
- **Service:** ${err.service_name}${err.function_name ? '.' + err.function_name : ''}
- **User:** ${err.user_email || 'N/A'} (${err.user_id || 'N/A'})

### Error Message
\`\`\`
${err.error_message}
\`\`\`

### Request Body
\`\`\`json
${err.request_body ? JSON.stringify(err.request_body, null, 2) : 'N/A'}
\`\`\`

### Stacktrace
\`\`\`
${err.stacktrace || 'N/A'}
\`\`\``
    navigator.clipboard.writeText(text)
  }

  const sourceBadge = (source: string) => {
    const colors: Record<string, string> = {
      unhandled: 'bg-red-100 text-red-800',
      swallowed: 'bg-yellow-100 text-yellow-800',
      manual: 'bg-blue-100 text-blue-800',
    }
    return (
      <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${colors[source] || 'bg-gray-100 text-gray-800'}`}>
        {source}
      </span>
    )
  }

  const totalPages = Math.ceil(errorLogsTotal / perPage)

  // --- Render ---

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
          {/* Toolbar */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
            <div className="flex items-center gap-3 flex-wrap">
              <p className="text-lg text-gray-600">
                {filteredUsers.length} user{filteredUsers.length !== 1 ? 's' : ''}
                {searchQuery && ` (filtered from ${users.length})`}
              </p>
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              <button
                onClick={() => setShowCreateModal(true)}
                className="py-2 px-4 bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-semibold rounded-lg transition-colors text-base"
                style={{ minHeight: '44px' }}
              >
                Create User
              </button>
              <button
                onClick={exportCSV}
                className="py-2 px-4 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold rounded-lg transition-colors text-base"
                style={{ minHeight: '44px' }}
              >
                Export CSV
              </button>
            </div>
          </div>

          {/* Search bar */}
          <div className="mb-4">
            <input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder="Search by email or name..."
              className="w-full border border-gray-300 rounded-lg px-4 py-3 text-base"
              style={{ minHeight: '44px' }}
            />
          </div>

          {filteredUsers.length === 0 ? (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <p className="text-xl text-gray-600">
                {searchQuery ? 'No users match your search.' : 'No users found.'}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredUsers.map(u => (
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

                  {/* Subscription info */}
                  {(u.subscription_plan || u.subscription_current_period_end) && (
                    <div className="flex items-center gap-4 mt-3 text-base text-gray-600">
                      {u.subscription_plan && (
                        <span>Plan: <strong className="text-gray-900 capitalize">{u.subscription_plan}</strong></span>
                      )}
                      {u.subscription_current_period_end && (
                        <span>Renews: <strong className="text-gray-900">{new Date(u.subscription_current_period_end).toLocaleDateString()}</strong></span>
                      )}
                    </div>
                  )}

                  {u.last_active_at && (
                    <p className="text-base text-gray-500 mt-3">
                      Last active: {new Date(u.last_active_at).toLocaleDateString()}
                    </p>
                  )}

                  {/* Action buttons */}
                  <div className="flex items-center gap-3 mt-4 pt-3 border-t border-gray-100 flex-wrap">
                    <button
                      onClick={() => openEditModal(u)}
                      className="py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors text-base"
                      style={{ minHeight: '44px' }}
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleToggle(u)}
                      className={`py-2 px-4 font-semibold rounded-lg transition-colors text-base text-white ${
                        u.account_status === 'admin_disabled'
                          ? 'bg-green-600 hover:bg-green-700'
                          : 'bg-yellow-600 hover:bg-yellow-700'
                      }`}
                      style={{ minHeight: '44px' }}
                    >
                      {u.account_status === 'admin_disabled' ? 'Enable' : 'Disable'}
                    </button>
                    <button
                      onClick={() => handleDelete(u.id, u.email)}
                      className="py-2 px-4 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors text-base"
                      style={{ minHeight: '44px' }}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Create User Modal */}
      <Modal open={showCreateModal} onClose={() => setShowCreateModal(false)} title="Create User">
        <form onSubmit={handleCreateUser} className="space-y-4">
          <div>
            <label className="block text-base font-semibold text-gray-700 mb-1">Email *</label>
            <input
              type="email"
              required
              value={createForm.email}
              onChange={e => setCreateForm(prev => ({ ...prev, email: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-base"
              style={{ minHeight: '44px' }}
            />
          </div>
          <div>
            <label className="block text-base font-semibold text-gray-700 mb-1">Password *</label>
            <input
              type="password"
              required
              minLength={6}
              value={createForm.password}
              onChange={e => setCreateForm(prev => ({ ...prev, password: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-base"
              style={{ minHeight: '44px' }}
            />
          </div>
          <div>
            <label className="block text-base font-semibold text-gray-700 mb-1">Full Name</label>
            <input
              type="text"
              value={createForm.full_name || ''}
              onChange={e => setCreateForm(prev => ({ ...prev, full_name: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-base"
              style={{ minHeight: '44px' }}
            />
          </div>
          <div>
            <label className="block text-base font-semibold text-gray-700 mb-1">Account Status</label>
            <select
              value={createForm.account_status}
              onChange={e => setCreateForm(prev => ({ ...prev, account_status: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-base"
              style={{ minHeight: '44px' }}
            >
              <option value="trial">Trial</option>
              <option value="paid">Paid</option>
            </select>
          </div>
          {createForm.account_status === 'trial' && (
            <div>
              <label className="block text-base font-semibold text-gray-700 mb-1">Trial Days</label>
              <input
                type="number"
                min={1}
                max={365}
                value={createForm.trial_days || 14}
                onChange={e => setCreateForm(prev => ({ ...prev, trial_days: parseInt(e.target.value) || 14 }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-base"
                style={{ minHeight: '44px' }}
              />
            </div>
          )}
          {createForm.account_status === 'paid' && (
            <div>
              <label className="block text-base font-semibold text-gray-700 mb-1">Subscription Plan</label>
              <select
                value={createForm.subscription_plan || ''}
                onChange={e => setCreateForm(prev => ({ ...prev, subscription_plan: e.target.value || undefined }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-base"
                style={{ minHeight: '44px' }}
              >
                <option value="">None</option>
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>
          )}
          <div className="flex justify-end gap-3 pt-3">
            <button
              type="button"
              onClick={() => setShowCreateModal(false)}
              className="py-2 px-4 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold rounded-lg transition-colors text-base"
              style={{ minHeight: '44px' }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={creating}
              className="py-2 px-4 bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-semibold rounded-lg transition-colors text-base disabled:opacity-50"
              style={{ minHeight: '44px' }}
            >
              {creating ? 'Creating...' : 'Create User'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Edit User Modal */}
      <Modal open={!!editUser} onClose={() => setEditUser(null)} title="Edit User">
        <form onSubmit={handleUpdateUser} className="space-y-4">
          <div>
            <label className="block text-base font-semibold text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={editForm.email || ''}
              onChange={e => setEditForm(prev => ({ ...prev, email: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-base"
              style={{ minHeight: '44px' }}
            />
          </div>
          <div>
            <label className="block text-base font-semibold text-gray-700 mb-1">New Password (leave blank to keep)</label>
            <input
              type="password"
              value={editForm.password || ''}
              onChange={e => setEditForm(prev => ({ ...prev, password: e.target.value }))}
              placeholder="Leave blank to keep current"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-base"
              style={{ minHeight: '44px' }}
            />
          </div>
          <div>
            <label className="block text-base font-semibold text-gray-700 mb-1">Full Name</label>
            <input
              type="text"
              value={editForm.full_name || ''}
              onChange={e => setEditForm(prev => ({ ...prev, full_name: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-base"
              style={{ minHeight: '44px' }}
            />
          </div>
          <div>
            <label className="block text-base font-semibold text-gray-700 mb-1">Account Status</label>
            <select
              value={editForm.account_status || ''}
              onChange={e => setEditForm(prev => ({ ...prev, account_status: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-base"
              style={{ minHeight: '44px' }}
            >
              <option value="trial">Trial</option>
              <option value="paid">Paid</option>
              <option value="cancelled">Canceled</option>
              <option value="past_due">Past Due</option>
              <option value="admin_disabled">Disabled</option>
            </select>
          </div>
          <div>
            <label className="block text-base font-semibold text-gray-700 mb-1">Subscription Plan</label>
            <select
              value={editForm.subscription_plan || ''}
              onChange={e => setEditForm(prev => ({ ...prev, subscription_plan: e.target.value }))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-base"
              style={{ minHeight: '44px' }}
            >
              <option value="">None</option>
              <option value="monthly">Monthly</option>
              <option value="yearly">Yearly</option>
            </select>
          </div>
          {(editForm.account_status === 'trial' || (!editForm.account_status && editUser?.account_status === 'trial')) && (
            <div>
              <label className="block text-base font-semibold text-gray-700 mb-1">Trial End Date</label>
              <input
                type="date"
                value={editForm.trial_ends_at || ''}
                onChange={e => setEditForm(prev => ({ ...prev, trial_ends_at: e.target.value }))}
                min={new Date().toISOString().split('T')[0]}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-base"
                style={{ minHeight: '44px' }}
              />
            </div>
          )}
          <div className="flex justify-end gap-3 pt-3">
            <button
              type="button"
              onClick={() => setEditUser(null)}
              className="py-2 px-4 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold rounded-lg transition-colors text-base"
              style={{ minHeight: '44px' }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={editing}
              className="py-2 px-4 bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-semibold rounded-lg transition-colors text-base disabled:opacity-50"
              style={{ minHeight: '44px' }}
            >
              {editing ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Error Logs tab */}
      {activeTab === 'errors' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <p className="text-lg text-gray-600">
              Error Logs ({errorLogsTotal})
            </p>
            <button
              onClick={() => loadErrorLogs(errorLogsPage)}
              className="py-2 px-4 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold rounded-lg transition-colors text-base"
              style={{ minHeight: '44px' }}
            >
              Refresh
            </button>
          </div>

          {/* Filters */}
          <div className="flex gap-3 mb-6 items-center flex-wrap">
            <form onSubmit={handleErrorSearch} className="flex gap-2">
              <input
                type="text"
                value={errorSearch}
                onChange={(e) => setErrorSearch(e.target.value)}
                placeholder="Search error messages..."
                className="border border-gray-300 rounded-lg px-3 py-2 text-base w-64"
                style={{ minHeight: '44px' }}
              />
              <button
                type="submit"
                className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white px-4 py-2 rounded-lg text-base font-semibold"
                style={{ minHeight: '44px' }}
              >
                Search
              </button>
            </form>

            <select
              value={errorSourceFilter}
              onChange={(e) => { setErrorSourceFilter(e.target.value); setTimeout(() => loadErrorLogs(1), 0) }}
              className="border border-gray-300 rounded-lg px-3 py-2 text-base"
              style={{ minHeight: '44px' }}
            >
              <option value="">All sources</option>
              <option value="unhandled">Unhandled</option>
              <option value="swallowed">Swallowed</option>
              <option value="manual">Manual</option>
            </select>

            <label className="flex items-center gap-2 text-base cursor-pointer" style={{ minHeight: '44px' }}>
              <input
                type="checkbox"
                checked={showResolved}
                onChange={(e) => { setShowResolved(e.target.checked); setTimeout(() => loadErrorLogs(1), 0) }}
                className="w-5 h-5"
              />
              Show resolved
            </label>
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
              <p className="text-xl text-gray-600">No errors found.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {errorLogs.map(log => (
                <div key={log.id} className="border border-gray-200 rounded-lg overflow-hidden">
                  <button
                    onClick={() => setExpandedLogId(expandedLogId === log.id ? null : log.id)}
                    className="w-full text-left p-4 hover:bg-gray-50 transition-colors"
                    style={{ minHeight: '44px' }}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 flex-wrap mb-1">
                          {sourceBadge(log.source)}
                          {log.status_code && (
                            <span className="inline-block px-2 py-0.5 text-xs font-mono font-semibold rounded bg-gray-100 text-gray-800">
                              {log.status_code}
                            </span>
                          )}
                          <span className="text-base font-semibold text-gray-900">
                            {log.http_method} {log.endpoint}
                          </span>
                          {log.is_resolved && (
                            <span className="text-green-600 text-xs font-medium">Resolved</span>
                          )}
                        </div>
                        <p className="text-base text-gray-700 truncate">{log.error_message}</p>
                      </div>
                      <span className="text-sm text-gray-500 flex-shrink-0 whitespace-nowrap">
                        {new Date(log.created_at).toLocaleString()}
                      </span>
                    </div>
                  </button>

                  {/* Expanded detail */}
                  {expandedLogId === log.id && (
                    <div className="px-4 pb-4 pt-2 border-t border-gray-100 bg-gray-50">
                      <div className="space-y-4">
                        {/* Error message */}
                        <div>
                          <h4 className="font-semibold text-base mb-1">Error Message</h4>
                          <pre className="bg-white border border-gray-200 rounded-lg p-3 text-sm whitespace-pre-wrap break-words">
                            {log.error_message}
                          </pre>
                        </div>

                        {/* Context grid */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-base">
                          <div>
                            <span className="text-gray-500">Type:</span>{' '}
                            <span className="font-medium">{log.error_type || 'N/A'}</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Status Code:</span>{' '}
                            <span className="font-medium">{log.status_code || 'N/A'}</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Service:</span>{' '}
                            <span className="font-medium">{log.service_name || 'N/A'}</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Function:</span>{' '}
                            <span className="font-medium">{log.function_name || 'N/A'}</span>
                          </div>
                          <div>
                            <span className="text-gray-500">User:</span>{' '}
                            <span className="font-medium">{log.user_email || log.user_id || 'N/A'}</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Environment:</span>{' '}
                            <span className="font-medium">{log.environment || 'N/A'}</span>
                          </div>
                        </div>

                        {/* Request body */}
                        {log.request_body && (
                          <div>
                            <h4 className="font-semibold text-base mb-1">Request Body</h4>
                            <pre className="bg-white border border-gray-200 rounded-lg p-3 text-sm whitespace-pre-wrap break-words overflow-x-auto">
                              {JSON.stringify(log.request_body, null, 2)}
                            </pre>
                          </div>
                        )}

                        {/* Query params */}
                        {log.query_params && (
                          <div>
                            <h4 className="font-semibold text-base mb-1">Query Parameters</h4>
                            <pre className="bg-white border border-gray-200 rounded-lg p-3 text-sm whitespace-pre-wrap break-words">
                              {JSON.stringify(log.query_params, null, 2)}
                            </pre>
                          </div>
                        )}

                        {/* Stacktrace */}
                        {log.stacktrace && (
                          <div>
                            <h4 className="font-semibold text-base mb-1">Stacktrace</h4>
                            <pre className="bg-gray-900 text-green-400 rounded-lg p-4 text-sm whitespace-pre-wrap break-words overflow-x-auto">
                              {log.stacktrace}
                            </pre>
                          </div>
                        )}

                        {/* Resolution info */}
                        {log.is_resolved && (
                          <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-base">
                            <strong>Resolved by:</strong> {log.resolved_by} at{' '}
                            {log.resolved_at && new Date(log.resolved_at).toLocaleString()}
                            {log.notes && <p className="mt-1"><strong>Notes:</strong> {log.notes}</p>}
                          </div>
                        )}

                        {/* Actions */}
                        <div className="flex gap-2 items-center flex-wrap">
                          <button
                            onClick={() => copyForAI(log)}
                            className="py-2 px-4 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold rounded-lg transition-colors text-base"
                            style={{ minHeight: '44px' }}
                          >
                            Copy for AI
                          </button>

                          {log.is_resolved ? (
                            <button
                              onClick={() => handleUnresolve(log.id)}
                              className="py-2 px-4 bg-yellow-500 hover:bg-yellow-600 text-white font-semibold rounded-lg transition-colors text-base"
                              style={{ minHeight: '44px' }}
                            >
                              Reopen
                            </button>
                          ) : (
                            <>
                              <input
                                type="text"
                                value={resolveNotes}
                                onChange={(e) => setResolveNotes(e.target.value)}
                                placeholder="Resolution notes (optional)"
                                className="border border-gray-300 rounded-lg px-3 py-2 text-base w-64"
                                style={{ minHeight: '44px' }}
                              />
                              <button
                                onClick={() => handleResolve(log.id)}
                                disabled={resolving}
                                className="py-2 px-4 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors text-base disabled:opacity-50"
                                style={{ minHeight: '44px' }}
                              >
                                {resolving ? 'Resolving...' : 'Resolve'}
                              </button>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-3 mt-6">
              <button
                onClick={() => loadErrorLogs(errorLogsPage - 1)}
                disabled={errorLogsPage <= 1}
                className="py-2 px-4 border border-gray-300 rounded-lg text-base font-semibold disabled:opacity-50 hover:bg-gray-50 transition-colors"
                style={{ minHeight: '44px' }}
              >
                Previous
              </button>
              <span className="text-base text-gray-600">
                Page {errorLogsPage} of {totalPages}
              </span>
              <button
                onClick={() => loadErrorLogs(errorLogsPage + 1)}
                disabled={errorLogsPage >= totalPages}
                className="py-2 px-4 border border-gray-300 rounded-lg text-base font-semibold disabled:opacity-50 hover:bg-gray-50 transition-colors"
                style={{ minHeight: '44px' }}
              >
                Next
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
