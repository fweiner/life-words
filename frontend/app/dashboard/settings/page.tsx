'use client'

import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'next/navigation'
import { createClient } from '@/lib/supabase'
import { apiClient } from '@/lib/api/client'
import Link from 'next/link'
import { useSubscription } from '@/lib/hooks/useSubscription'

interface AccommodationSettings {
  match_acceptable_alternatives: boolean
  match_partial_substring: boolean
  match_word_overlap: boolean
  match_stop_word_filtering: boolean
  match_synonyms: boolean
  match_first_name_only: boolean
}

const DEFAULT_ACCOMMODATIONS: AccommodationSettings = {
  match_acceptable_alternatives: true,
  match_partial_substring: true,
  match_word_overlap: true,
  match_stop_word_filtering: true,
  match_synonyms: true,
  match_first_name_only: true,
}

const ACCOMMODATION_INFO = [
  {
    key: 'match_acceptable_alternatives' as const,
    label: 'Acceptable Alternatives',
    description: 'Accept predefined alternative answers (e.g., "dad" for "father")'
  },
  {
    key: 'match_partial_substring' as const,
    label: 'Partial Matching',
    description: 'Accept answers where response contains expected answer or vice versa'
  },
  {
    key: 'match_word_overlap' as const,
    label: 'Word Overlap',
    description: 'Accept answers with 50% or more matching words'
  },
  {
    key: 'match_stop_word_filtering' as const,
    label: 'Stop Word Filtering',
    description: 'Ignore filler words like "the", "a", "when", "we" when comparing'
  },
  {
    key: 'match_synonyms' as const,
    label: 'Synonym Matching',
    description: 'Accept similar words (e.g., "kind" for "nice", "home" for "house")'
  },
  {
    key: 'match_first_name_only' as const,
    label: 'First Name Only',
    description: 'Accept just the first name when a full name is expected'
  },
]

export default function SettingsPage() {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [voiceGender, setVoiceGender] = useState<'male' | 'female' | 'neutral'>('female')
  const [accommodations, setAccommodations] = useState<AccommodationSettings>(DEFAULT_ACCOMMODATIONS)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [portalLoading, setPortalLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const supabase = createClient()
  const searchParams = useSearchParams()
  const { subscription, refresh: refreshSubscription } = useSubscription()
  const [checkoutLoading, setCheckoutLoading] = useState(false)

  // Show success banner if redirected from Stripe checkout
  useEffect(() => {
    if (searchParams.get('subscription') === 'success') {
      setSuccess('Subscription activated successfully! Thank you.')
      refreshSubscription()
    }
  }, [searchParams, refreshSubscription])

  const handleSubscribe = async (plan: string) => {
    setCheckoutLoading(true)
    try {
      const data = await apiClient.post<{ checkout_url: string }>('/api/stripe/checkout', { plan })
      window.location.href = data.checkout_url
    } catch (err) {
      console.error('Error creating checkout:', err)
      setError(err instanceof Error ? err.message : 'Failed to start checkout')
      setCheckoutLoading(false)
    }
  }

  const handleManageSubscription = async () => {
    setPortalLoading(true)
    try {
      const data = await apiClient.post<{ portal_url: string }>('/api/stripe/portal')
      window.location.href = data.portal_url
    } catch (err) {
      console.error('Error opening portal:', err)
      setError(err instanceof Error ? err.message : 'Failed to open subscription management')
      setPortalLoading(false)
    }
  }

  const loadProfile = useCallback(async () => {
    try {
      // Get user email from auth
      const { data: { user } } = await supabase.auth.getUser()
      if (user) {
        setEmail(user.email || '')
      }

      // Get profile from API
      const profile = await apiClient.get<Record<string, unknown>>('/api/profile')
      setFullName((profile.full_name as string) || '')
      setVoiceGender((profile.voice_gender as 'male' | 'female' | 'neutral') || 'female')
      setAccommodations({
        match_acceptable_alternatives: (profile.match_acceptable_alternatives as boolean) ?? true,
        match_partial_substring: (profile.match_partial_substring as boolean) ?? true,
        match_word_overlap: (profile.match_word_overlap as boolean) ?? true,
        match_stop_word_filtering: (profile.match_stop_word_filtering as boolean) ?? true,
        match_synonyms: (profile.match_synonyms as boolean) ?? true,
        match_first_name_only: (profile.match_first_name_only as boolean) ?? true,
      })
    } catch (err) {
      console.error('Error loading profile:', err)
      setError('Failed to load profile')
    } finally {
      setLoading(false)
    }
  }, [supabase.auth])

  useEffect(() => {
    loadProfile()
  }, [loadProfile])

  const handleAccommodationToggle = (key: keyof AccommodationSettings) => {
    setAccommodations(prev => ({
      ...prev,
      [key]: !prev[key]
    }))
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setSaving(true)

    try {
      await apiClient.patch('/api/profile', {
        full_name: fullName,
        voice_gender: voiceGender,
        ...accommodations
      })

      setSuccess('Settings saved successfully!')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to save changes')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="text-center text-xl">Loading...</div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-8">
      <div className="mb-6">
        <Link
          href="/dashboard"
          className="text-[var(--color-primary)] hover:text-[var(--color-accent)] font-medium text-lg"
        >
          &larr; Back to Dashboard
        </Link>
      </div>

      <h1 className="text-3xl font-bold mb-8 text-[var(--color-primary)]">
        Settings
      </h1>

      {error && (
        <div
          className="mb-6 p-4 bg-red-50 border-2 border-red-200 rounded-lg text-red-800"
          role="alert"
        >
          <p className="font-semibold">Error</p>
          <p>{error}</p>
        </div>
      )}

      {success && (
        <div
          className="mb-6 p-4 bg-green-50 border-2 border-green-200 rounded-lg text-green-800"
          role="alert"
        >
          <p>{success}</p>
        </div>
      )}

      {/* Subscription Section */}
      {subscription && (
        <div className="mb-8 p-6 border-2 border-gray-200 rounded-lg">
          <h2 className="text-xl font-bold mb-4 text-gray-900">Subscription</h2>

          {subscription.is_paid && (
            <div>
              <p className="text-lg text-gray-700 mb-1">
                <span className="font-semibold text-green-700">Active</span> &mdash;{' '}
                {subscription.subscription_plan === 'yearly' ? 'Yearly' : 'Monthly'} plan
              </p>
              {subscription.subscription_current_period_end && (
                <p className="text-base text-gray-500 mb-4">
                  Next billing date: {new Date(subscription.subscription_current_period_end).toLocaleDateString()}
                </p>
              )}
              <button
                onClick={handleManageSubscription}
                disabled={portalLoading}
                className="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg text-lg transition-colors focus:outline-none focus:ring-4 focus:ring-gray-300 focus:ring-offset-2"
                style={{ minHeight: '44px' }}
              >
                {portalLoading ? 'Opening...' : 'Manage Subscription'}
              </button>
            </div>
          )}

          {subscription.is_trial_active && !subscription.is_paid && (
            <div>
              <p className="text-lg text-gray-700 mb-1">
                <span className="font-semibold text-blue-700">Free Trial</span>
                {subscription.trial_ends_at && (
                  <> &mdash; {Math.max(0, Math.ceil((new Date(subscription.trial_ends_at).getTime() - Date.now()) / (1000 * 60 * 60 * 24)))} days remaining</>
                )}
              </p>
              <p className="text-base text-gray-500 mb-4">
                Subscribe now to continue practicing after your trial ends.
              </p>
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() => handleSubscribe('monthly')}
                  disabled={checkoutLoading}
                  className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg text-lg transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                  style={{ minHeight: '44px' }}
                >
                  {checkoutLoading ? 'Loading...' : 'Monthly ($9.95/mo)'}
                </button>
                <button
                  onClick={() => handleSubscribe('yearly')}
                  disabled={checkoutLoading}
                  className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg text-lg transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                  style={{ minHeight: '44px' }}
                >
                  {checkoutLoading ? 'Loading...' : 'Yearly ($99.95/yr)'}
                </button>
              </div>
            </div>
          )}

          {!subscription.is_paid && !subscription.is_trial_active && (
            <div>
              <p className="text-lg text-gray-700 mb-1">
                <span className="font-semibold text-amber-700">
                  {subscription.account_status === 'cancelled' ? 'Cancelled' :
                   subscription.account_status === 'past_due' ? 'Payment Failed' :
                   'Trial Ended'}
                </span>
              </p>
              <p className="text-base text-gray-500 mb-4">
                {subscription.account_status === 'past_due'
                  ? 'Please update your payment method to continue practicing.'
                  : 'Subscribe to access practice sessions.'}
              </p>
              <div className="flex flex-col sm:flex-row gap-3">
                {subscription.has_subscription && subscription.account_status === 'past_due' ? (
                  <button
                    onClick={handleManageSubscription}
                    disabled={portalLoading}
                    className="bg-amber-600 hover:bg-amber-700 disabled:bg-amber-400 text-white font-semibold py-3 px-6 rounded-lg text-lg transition-colors focus:outline-none focus:ring-4 focus:ring-amber-300 focus:ring-offset-2"
                    style={{ minHeight: '44px' }}
                  >
                    {portalLoading ? 'Opening...' : 'Update Payment Method'}
                  </button>
                ) : (
                  <>
                    <button
                      onClick={() => handleSubscribe('monthly')}
                      disabled={checkoutLoading}
                      className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg text-lg transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                      style={{ minHeight: '44px' }}
                    >
                      {checkoutLoading ? 'Loading...' : 'Monthly ($9.95/mo)'}
                    </button>
                    <button
                      onClick={() => handleSubscribe('yearly')}
                      disabled={checkoutLoading}
                      className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg text-lg transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                      style={{ minHeight: '44px' }}
                    >
                      {checkoutLoading ? 'Loading...' : 'Yearly ($99.95/yr)'}
                    </button>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-8">
        {/* Profile Section */}
        <div className="max-w-xl">
          <h2 className="text-xl font-bold mb-4 text-gray-900">Profile</h2>

          <div className="space-y-4">
            <div>
              <label
                htmlFor="email"
                className="block text-lg font-medium mb-2"
              >
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                disabled
                className="w-full px-4 py-3 text-lg border-2 border-gray-200 rounded-lg bg-gray-50 text-gray-600"
              />
              <p className="mt-2 text-sm text-gray-500">
                Email cannot be changed
              </p>
            </div>

            <div>
              <label
                htmlFor="fullName"
                className="block text-lg font-medium mb-2"
              >
                Full Name
              </label>
              <input
                id="fullName"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                placeholder="Your full name"
              />
              <p className="mt-2 text-sm text-gray-500">
                This name is used when sending invites to contacts
              </p>
            </div>
          </div>
        </div>

        {/* Voice Section */}
        <div className="max-w-xl">
          <h2 className="text-xl font-bold mb-4 text-gray-900">Voice Preference</h2>
          <p className="text-sm text-gray-500 mb-3">
            Choose the voice used when the app speaks to you
          </p>
          <div className="flex flex-col sm:flex-row gap-3">
            <label className={`flex items-center justify-center px-6 py-4 border-2 rounded-lg cursor-pointer transition-colors ${voiceGender === 'female' ? 'border-[var(--color-primary)] bg-blue-50' : 'border-gray-300 hover:border-gray-400'}`}>
              <input
                type="radio"
                name="voiceGender"
                value="female"
                checked={voiceGender === 'female'}
                onChange={(e) => setVoiceGender(e.target.value as 'female')}
                className="sr-only"
              />
              <span className="text-2xl mr-3">👩</span>
              <span className="text-lg font-medium">Female Voice</span>
            </label>
            <label className={`flex items-center justify-center px-6 py-4 border-2 rounded-lg cursor-pointer transition-colors ${voiceGender === 'male' ? 'border-[var(--color-primary)] bg-blue-50' : 'border-gray-300 hover:border-gray-400'}`}>
              <input
                type="radio"
                name="voiceGender"
                value="male"
                checked={voiceGender === 'male'}
                onChange={(e) => setVoiceGender(e.target.value as 'male')}
                className="sr-only"
              />
              <span className="text-2xl mr-3">👨</span>
              <span className="text-lg font-medium">Male Voice</span>
            </label>
          </div>
        </div>

        {/* Answer Accommodations Section */}
        <div>
          <h2 className="text-xl font-bold mb-2 text-gray-900">Answer Matching</h2>
          <p className="text-sm text-gray-500 mb-4">
            These settings control how your spoken answers are evaluated. Turn off accommodations for stricter matching.
          </p>

          <div className="space-y-3 max-w-2xl">
            {ACCOMMODATION_INFO.map(({ key, label, description }) => (
              <label
                key={key}
                className={`flex items-start p-4 border-2 rounded-lg transition-colors cursor-pointer ${
                  accommodations[key]
                    ? 'border-green-300 bg-green-50'
                    : 'border-gray-200 bg-gray-50'
                }`}
              >
                <input
                  type="checkbox"
                  checked={accommodations[key]}
                  onChange={() => handleAccommodationToggle(key)}
                  className="flex-shrink-0 w-6 h-6 mt-0.5 rounded border-2 border-gray-300 text-green-600 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 cursor-pointer"
                />
                <div className="ml-4 flex-1">
                  <div className="font-medium text-gray-900">{label}</div>
                  <div className="text-sm text-gray-600">{description}</div>
                </div>
              </label>
            ))}
          </div>

          <p className="mt-4 text-sm text-gray-500 italic">
            Note: Case-insensitive matching is always enabled.
          </p>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-semibold py-4 px-8 rounded-lg text-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
          style={{ minHeight: '44px' }}
        >
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </form>
    </div>
  )
}
