'use client'

import Link from 'next/link'
import { apiClient } from '@/lib/api/client'
import { useState } from 'react'

interface TrialBannerProps {
  accountStatus: string
  trialEndsAt: string | null
  isTrialActive: boolean
  isPaid: boolean
  canPractice: boolean
  hasSubscription: boolean
}

function getDaysRemaining(trialEndsAt: string | null): number | null {
  if (!trialEndsAt) return null
  const end = new Date(trialEndsAt)
  const now = new Date()
  const days = Math.ceil((end.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
  return Math.max(0, days)
}

export function TrialBanner({ accountStatus, trialEndsAt, isTrialActive, isPaid, canPractice, hasSubscription }: TrialBannerProps) {
  const [redirecting, setRedirecting] = useState(false)

  // Don't show banner for active paid subscribers
  if (isPaid) return null

  const daysRemaining = getDaysRemaining(trialEndsAt)

  const handleManageSubscription = async () => {
    setRedirecting(true)
    try {
      const data = await apiClient.post<{ portal_url: string }>('/api/stripe/portal')
      window.location.href = data.portal_url
    } catch (err) {
      console.error('Error opening portal:', err)
      setRedirecting(false)
    }
  }

  // Trial active - blue info banner
  if (isTrialActive && canPractice) {
    return (
      <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <p className="text-blue-800 text-lg font-semibold">
              Free Trial: {daysRemaining} {daysRemaining === 1 ? 'day' : 'days'} remaining
            </p>
            <p className="text-blue-700 text-base">
              Subscribe to keep practicing after your trial ends.
            </p>
          </div>
          <Link
            href="/pricing"
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg text-lg transition-colors whitespace-nowrap focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-offset-2"
            style={{ minHeight: '44px' }}
          >
            View Plans
          </Link>
        </div>
      </div>
    )
  }

  // Trial expired, cancelled, or past_due - amber warning banner
  if (!canPractice) {
    const isPastDue = accountStatus === 'past_due'
    return (
      <div className="bg-amber-50 border-2 border-amber-200 rounded-lg p-4 mb-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <p className="text-amber-800 text-lg font-semibold">
              {accountStatus === 'trial'
                ? 'Your free trial has ended'
                : isPastDue
                  ? 'Payment failed. Please update your payment method.'
                  : 'Subscription inactive'}
            </p>
            <p className="text-amber-700 text-base">
              {isPastDue
                ? 'Update your payment method to continue practicing.'
                : 'Subscribe to access practice sessions. You can still manage contacts and view progress.'}
            </p>
          </div>
          {isPastDue && hasSubscription ? (
            <button
              onClick={handleManageSubscription}
              disabled={redirecting}
              className="bg-amber-600 hover:bg-amber-700 disabled:bg-amber-400 text-white font-semibold py-3 px-6 rounded-lg text-lg transition-colors whitespace-nowrap focus:outline-none focus:ring-4 focus:ring-amber-300 focus:ring-offset-2"
              style={{ minHeight: '44px' }}
            >
              {redirecting ? 'Opening...' : 'Manage Subscription'}
            </button>
          ) : (
            <Link
              href="/pricing"
              className="bg-amber-600 hover:bg-amber-700 text-white font-semibold py-3 px-6 rounded-lg text-lg transition-colors whitespace-nowrap focus:outline-none focus:ring-4 focus:ring-amber-300 focus:ring-offset-2"
              style={{ minHeight: '44px' }}
            >
              View Plans
            </Link>
          )}
        </div>
      </div>
    )
  }

  return null
}
