'use client'

import { useState } from 'react'
import { apiClient } from '@/lib/api/client'
import Link from 'next/link'

interface CheckoutResponse {
  checkout_url: string
}

const PLANS = [
  {
    id: 'monthly',
    name: 'Monthly',
    price: '$9.95',
    interval: '/month',
    description: 'Flexible monthly billing',
    badge: null,
  },
  {
    id: 'yearly',
    name: 'Yearly',
    price: '$99.95',
    interval: '/year',
    description: 'Best value — save ~17%',
    badge: 'Best Value',
  },
]

export default function SubscribePage() {
  const [loading, setLoading] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubscribe = async (planId: string) => {
    setLoading(planId)
    setError(null)

    try {
      const data = await apiClient.post<CheckoutResponse>('/api/stripe/checkout', {
        plan: planId,
      })
      window.location.assign(data.checkout_url)
    } catch (err: unknown) {
      const e = err as Record<string, unknown>
      setError((e.detail as string) || (e.message as string) || 'Failed to start checkout')
      setLoading(null)
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="mb-6">
          <Link
            href="/dashboard"
            className="text-[var(--color-primary)] hover:text-[var(--color-accent)] font-medium text-lg"
          >
            &larr; Back to Dashboard
          </Link>
        </div>

        <h1 className="text-3xl font-bold mb-4 text-[var(--color-primary)] text-center">
          Choose Your Plan
        </h1>
        <p className="text-xl text-gray-700 mb-8 text-center">
          Continue practicing with Life Words. Cancel anytime.
        </p>

        {error && (
          <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 mb-6">
            <p className="text-red-700 text-lg font-semibold">Error: {error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-2xl mx-auto">
          {PLANS.map((plan) => (
            <div
              key={plan.id}
              className={`relative border-2 rounded-lg p-6 text-center ${
                plan.badge
                  ? 'border-[var(--color-primary)] bg-blue-50'
                  : 'border-gray-200'
              }`}
            >
              {plan.badge && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[var(--color-primary)] text-white text-sm font-bold px-4 py-1 rounded-full">
                  {plan.badge}
                </div>
              )}

              <h2 className="text-2xl font-bold text-gray-900 mb-2 mt-2">
                {plan.name}
              </h2>
              <div className="mb-4">
                <span className="text-4xl font-bold text-gray-900">{plan.price}</span>
                <span className="text-lg text-gray-600">{plan.interval}</span>
              </div>
              <p className="text-base text-gray-600 mb-6">{plan.description}</p>

              <button
                onClick={() => handleSubscribe(plan.id)}
                disabled={loading !== null}
                className="w-full bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] disabled:bg-gray-400 text-white font-bold py-4 px-6 rounded-lg text-xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                style={{ minHeight: '44px' }}
              >
                {loading === plan.id ? 'Redirecting...' : 'Subscribe'}
              </button>
            </div>
          ))}
        </div>

        <div className="mt-8 text-center text-base text-gray-600">
          <p>All plans include full access to Name Practice, Question Practice, and Information Practice.</p>
          <p className="mt-2">Secure payment powered by Stripe. Cancel anytime from your settings.</p>
        </div>
      </div>
    </div>
  )
}
