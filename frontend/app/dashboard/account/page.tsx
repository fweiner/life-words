'use client'

import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase'
import { apiClient } from '@/lib/api/client'
import { useSubscription } from '@/lib/hooks/useSubscription'
import Link from 'next/link'

export default function AccountPage() {
  const [email, setEmail] = useState('')
  const [resetSending, setResetSending] = useState(false)
  const [resetMessage, setResetMessage] = useState('')
  const [portalLoading, setPortalLoading] = useState(false)
  const [portalError, setPortalError] = useState('')
  const [showEmail, setShowEmail] = useState(false)
  const supabase = createClient()
  const { subscription, loading: subLoading } = useSubscription()

  useEffect(() => {
    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      if (user?.email) {
        setEmail(user.email)
      }
    }
    getUser()
  }, [supabase.auth])

  const handlePasswordReset = async () => {
    if (!email) return
    setResetSending(true)
    setResetMessage('')
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/update-password`,
      })
      if (error) throw error
      setResetMessage('Password reset email sent! Check your inbox.')
    } catch {
      setResetMessage('Failed to send reset email. Please try again.')
    } finally {
      setResetSending(false)
    }
  }

  const handleManageSubscription = async () => {
    setPortalLoading(true)
    setPortalError('')
    try {
      const data = await apiClient.post<{ portal_url: string }>('/api/stripe/portal')
      window.location.href = data.portal_url
    } catch {
      setPortalError('No active billing account found. Please contact support.')
      setPortalLoading(false)
    }
  }

  const subscriptionLabel = () => {
    if (subLoading) return 'Loading...'
    if (!subscription) return 'Unknown'
    if (subscription.is_paid) return 'Active'
    if (subscription.is_trial_active) return 'Free Trial'
    if (subscription.account_status === 'cancelled') return 'Cancelled'
    if (subscription.account_status === 'past_due') return 'Payment Failed'
    return 'Inactive'
  }

  const planLabel = () => {
    if (!subscription) return '—'
    if (subscription.subscription_plan === 'yearly') return 'Yearly ($99.95/yr)'
    if (subscription.subscription_plan === 'monthly') return 'Monthly ($9.95/mo)'
    if (subscription.is_trial_active) return 'Free Trial'
    if (subscription.is_paid) return 'Active'
    return '—'
  }

  const renewsOn = () => {
    if (!subscription?.subscription_current_period_end) return null
    return new Date(subscription.subscription_current_period_end).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  return (
    <div>
      <div className="mb-6">
        <Link
          href="/dashboard"
          className="text-[var(--color-primary)] hover:text-[var(--color-accent)] font-medium text-lg"
        >
          &larr; Back to Dashboard
        </Link>
      </div>

      <h1 className="text-3xl font-bold mb-8 text-[var(--color-primary)]">
        Manage My Account
      </h1>

      <div className="grid gap-6 sm:grid-cols-2">
        {/* Your Subscription */}
        <div className="bg-white rounded-lg shadow-md p-6 flex items-start space-x-4">
          <div className="flex-shrink-0 w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
            <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="text-xl font-bold text-gray-900">Your Subscription</h2>
            <p className="text-base text-gray-500 mt-1">Status: <span className="font-semibold">{subscriptionLabel()}</span></p>
            <p className="text-base text-gray-500">Plan: {planLabel()}</p>
            {renewsOn() && (
              <p className="text-base text-gray-500">Renews: {renewsOn()}</p>
            )}
          </div>
        </div>

        {/* Forgot Password */}
        <div className="bg-white rounded-lg shadow-md p-6 flex items-start space-x-4">
          <div className="flex-shrink-0 w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="text-xl font-bold text-gray-900">Forgot Password</h2>
            <p className="text-base text-gray-500 mt-1">Send a password reset link to your email</p>
            <button
              onClick={handlePasswordReset}
              disabled={resetSending}
              className="mt-3 text-[var(--color-primary)] hover:text-[var(--color-primary-hover)] font-semibold text-base transition-colors disabled:opacity-50"
              style={{ minHeight: '44px' }}
            >
              {resetSending ? 'Sending...' : 'Reset Password'}
            </button>
            {resetMessage && (
              <p className={`mt-2 text-sm ${resetMessage.includes('sent') ? 'text-green-600' : 'text-red-600'}`}>
                {resetMessage}
              </p>
            )}
          </div>
        </div>

        {/* Forgot Username */}
        <div className="bg-white rounded-lg shadow-md p-6 flex items-start space-x-4">
          <div className="flex-shrink-0 w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
            <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="text-xl font-bold text-gray-900">Forgot Username</h2>
            <p className="text-base text-gray-500 mt-1">Your username (email) is:</p>
            {showEmail ? (
              <p className="mt-2 text-base font-semibold text-gray-900 break-all">{email}</p>
            ) : (
              <button
                onClick={() => setShowEmail(true)}
                className="mt-3 text-[var(--color-primary)] hover:text-[var(--color-primary-hover)] font-semibold text-base transition-colors"
                style={{ minHeight: '44px' }}
              >
                Show My Username
              </button>
            )}
          </div>
        </div>

        {/* Cancel Subscription */}
        <div className="bg-white rounded-lg shadow-md p-6 flex items-start space-x-4">
          <div className="flex-shrink-0 w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
            <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="text-xl font-bold text-gray-900">Cancel Subscription</h2>
            <p className="text-base text-gray-500 mt-1">Manage or cancel your subscription</p>
            <button
              onClick={handleManageSubscription}
              disabled={portalLoading}
              className="mt-3 text-red-600 hover:text-red-700 font-semibold text-base transition-colors disabled:opacity-50"
              style={{ minHeight: '44px' }}
            >
              {portalLoading ? 'Opening...' : 'Manage Subscription'}
            </button>
            {portalError && (
              <p className="mt-2 text-sm text-red-600">{portalError}</p>
            )}
          </div>
        </div>

        {/* Have Questions? */}
        <div className="bg-white rounded-lg shadow-md p-6 flex items-start space-x-4">
          <div className="flex-shrink-0 w-12 h-12 rounded-full bg-yellow-100 flex items-center justify-center">
            <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="text-xl font-bold text-gray-900">Have Questions?</h2>
            <p className="text-base text-gray-500 mt-1">We&apos;re here to help</p>
            <a
              href="mailto:support@parrotsoftware.com"
              className="mt-3 inline-block text-[var(--color-primary)] hover:text-[var(--color-primary-hover)] font-semibold text-base transition-colors"
              style={{ minHeight: '44px', lineHeight: '44px' }}
            >
              Email Support
            </a>
          </div>
        </div>

        {/* Contact Us */}
        <div className="bg-white rounded-lg shadow-md p-6 flex items-start space-x-4">
          <div className="flex-shrink-0 w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center">
            <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="text-xl font-bold text-gray-900">Contact Us</h2>
            <p className="text-base text-gray-500 mt-1">Reach out to our team</p>
            <a
              href="mailto:support@parrotsoftware.com"
              className="mt-3 inline-block text-[var(--color-primary)] hover:text-[var(--color-primary-hover)] font-semibold text-base transition-colors"
              style={{ minHeight: '44px', lineHeight: '44px' }}
            >
              support@parrotsoftware.com
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
