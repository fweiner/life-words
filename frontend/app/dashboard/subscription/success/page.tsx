'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useSubscription } from '@/lib/hooks/useSubscription'

export default function SubscriptionSuccessPage() {
  const router = useRouter()
  const { subscription, loading } = useSubscription()

  useEffect(() => {
    // If subscription is loaded and user is paid, show success
    // If not paid after loading, may still be processing
  }, [subscription, loading])

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-xl text-gray-600">Verifying your subscription...</p>
        </div>
      </div>
    )
  }

  if (subscription?.is_paid) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="text-center">
          <div className="mb-6 text-6xl text-green-500">&#10003;</div>
          <h1 className="text-3xl font-bold mb-4 text-[var(--color-success)]">
            Subscription Active!
          </h1>
          <p className="text-lg mb-6 text-gray-700">
            Thank you for subscribing to Life Words. You now have full access to all practice sessions.
          </p>
          <Link
            href="/dashboard/treatments/life-words"
            className="inline-block bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold py-4 px-8 rounded-lg text-xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
            style={{ minHeight: '44px' }}
          >
            Start Practicing
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-8">
      <div className="text-center">
        <div className="mb-6 text-6xl">!</div>
        <h1 className="text-3xl font-bold mb-4 text-amber-600">
          Payment Processing
        </h1>
        <p className="text-lg mb-6 text-gray-700">
          Your payment is still being processed. This usually takes just a moment.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => router.refresh()}
            className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-semibold py-4 px-8 rounded-lg text-lg transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
            style={{ minHeight: '44px' }}
          >
            Check Again
          </button>
          <Link
            href="/dashboard"
            className="inline-block bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-4 px-8 rounded-lg text-lg transition-colors focus:outline-none focus:ring-4 focus:ring-gray-300 focus:ring-offset-2"
            style={{ minHeight: '44px' }}
          >
            Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}
