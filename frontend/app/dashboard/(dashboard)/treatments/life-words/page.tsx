'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api/client'
import Link from 'next/link'
import { UnreadBadge } from '@/components/messaging/UnreadBadge'
import { useSubscription } from '@/lib/hooks/useSubscription'

export const dynamic = 'force-dynamic'

interface LifeWordsStatus {
  contact_count: number
  item_count: number
  total_count: number
  can_start_session: boolean
  min_contacts_required: number
}

interface InformationStatus {
  can_start_session: boolean
  filled_fields_count: number
  min_fields_required: number
}

export default function LifeWordsPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [isStarting, setIsStarting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [status, setStatus] = useState<LifeWordsStatus | null>(null)
  const [infoStatus, setInfoStatus] = useState<InformationStatus | null>(null)
  const [showCategoryChoice, setShowCategoryChoice] = useState(false)
  const { subscription } = useSubscription()
  const canPractice = subscription?.can_practice !== false

  useEffect(() => {
    loadStatus()
  }, [])

  const loadStatus = async () => {
    try {
      const data = await apiClient.get<LifeWordsStatus>('/api/life-words/status')
      setStatus(data)

      // Also load information practice status
      try {
        const infoData = await apiClient.get<InformationStatus>('/api/life-words/information-status')
        setInfoStatus(infoData)
      } catch (infoErr) {
        console.warn('Could not load information status:', infoErr)
      }
    } catch (err: unknown) {
      const e = err as Record<string, unknown>
      setError((e.detail as string) || (e.message as string) || 'An error occurred')
      console.error('Error loading status:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleStartSession = () => {
    setError(null)
    const hasPeople = (status?.contact_count || 0) > 0
    const hasStuff = (status?.item_count || 0) > 0

    if (hasPeople && hasStuff) {
      setShowCategoryChoice(true)
    } else if (hasPeople) {
      startSessionWithCategory('people')
    } else {
      startSessionWithCategory('items')
    }
  }

  const startSessionWithCategory = async (category: string) => {
    setIsStarting(true)
    setShowCategoryChoice(false)
    setError(null)

    try {
      const sessionData = await apiClient.post<{ session: { id: string } }>('/api/life-words/sessions', { category })
      router.push(`/dashboard/treatments/life-words/session/${sessionData.session.id}`)

    } catch (err: unknown) {
      const e = err as Record<string, unknown>
      setError((e.detail as string) || (e.message as string) || 'An error occurred')
      console.error('Error creating session:', err)
    } finally {
      setIsStarting(false)
    }
  }

  const handleStartQuestionSession = async () => {
    setIsStarting(true)
    setError(null)

    try {
      const sessionData = await apiClient.post<{ session: { id: string } }>('/api/life-words/question-sessions', {})
      router.push(`/dashboard/treatments/life-words/questions/session/${sessionData.session.id}`)

    } catch (err: unknown) {
      const e = err as Record<string, unknown>
      setError((e.detail as string) || (e.message as string) || 'An error occurred')
      console.error('Error creating question session:', err)
    } finally {
      setIsStarting(false)
    }
  }

  const handleStartInformationSession = async () => {
    setIsStarting(true)
    setError(null)

    try {
      const sessionData = await apiClient.post<{ session: { id: string } }>('/api/life-words/information-sessions', {})
      router.push(`/dashboard/treatments/life-words/information/session/${sessionData.session.id}`)

    } catch (err: unknown) {
      const e = err as Record<string, unknown>
      setError((e.detail as string) || (e.message as string) || 'An error occurred')
      console.error('Error creating information session:', err)
    } finally {
      setIsStarting(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-xl text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  const needsSetup = !status?.can_start_session

  const formatEntrySummary = () => {
    const people = status?.contact_count || 0
    const items = status?.item_count || 0
    const parts: string[] = []
    if (people > 0) parts.push(`${people} ${people === 1 ? 'person' : 'people'}`)
    if (items > 0) parts.push(`${items} ${items === 1 ? 'item' : 'items'}`)
    return parts.join(' and ') || '0 entries'
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-8">
        <h1 className="text-4xl font-bold mb-4 text-[var(--color-primary)]">
          My Life Words and Memory
        </h1>
        <p className="text-xl text-gray-700 mb-8">
          Practice naming the people, pets, and things that matter most to you.
        </p>

        {needsSetup ? (
          // Setup flow - user needs to add contacts first
          <div className="bg-amber-50 border-2 border-amber-200 rounded-lg p-8 mb-6">
            {(status?.total_count || 0) === 0 ? (
              // First-time user - show welcome guide
              <>
                <div className="text-6xl mb-4">👋</div>
                <h2 className="text-3xl font-bold mb-4 text-gray-900">
                  Welcome to Life Words and Memory!
                </h2>
                <p className="text-lg text-gray-700 mb-6">
                  This tool helps you practice remembering the names of people, pets, and things
                  that matter most to you. Let&apos;s get you set up!
                </p>

                <div className="bg-white rounded-lg p-6 mb-6 text-left">
                  <h3 className="text-2xl font-bold mb-4 text-gray-900">
                    Quick Start Guide:
                  </h3>
                  <ol className="space-y-4 text-lg text-gray-700">
                    <li className="flex items-start">
                      <span className="bg-[var(--color-primary)] text-white rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0 font-bold">1</span>
                      <span><strong>Add contacts</strong> - Upload photos of family, friends, and pets along with their names and your relationship to them.</span>
                    </li>
                    <li className="flex items-start">
                      <span className="bg-[var(--color-primary)] text-white rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0 font-bold">2</span>
                      <span><strong>Add details</strong> - Include their personality, interests, and where you usually see them. This helps create better hints!</span>
                    </li>
                    <li className="flex items-start">
                      <span className="bg-[var(--color-primary)] text-white rounded-full w-8 h-8 flex items-center justify-center mr-3 flex-shrink-0 font-bold">3</span>
                      <span><strong>Start practicing</strong> - Once you have at least 2 contacts, you can begin Name Practice or Question Practice.</span>
                    </li>
                  </ol>
                </div>

                <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4 mb-6">
                  <p className="text-blue-800 text-lg">
                    <strong>New here?</strong> Read the{' '}
                    <Link href="/dashboard/treatments/life-words/how-it-works" className="underline hover:text-blue-600">
                      How It Works guide
                    </Link>{' '}
                    to learn more about the different practice types and features.
                  </p>
                </div>

                <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center flex-wrap">
                  <Link
                    href="/dashboard/treatments/life-words/setup"
                    className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold py-6 px-12 rounded-lg text-2xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2 inline-block text-center"
                    style={{ minHeight: '44px' }}
                  >
                    Add Your First Contact
                  </Link>

                  <Link
                    href="/dashboard/treatments/life-words/how-it-works"
                    className="bg-blue-50 hover:bg-blue-100 text-blue-700 font-bold py-6 px-8 rounded-lg text-xl transition-colors focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-offset-2 inline-block text-center"
                    style={{ minHeight: '44px' }}
                  >
                    How It Works
                  </Link>
                </div>
              </>
            ) : (
              // User has some contacts but not enough
              <>
                <div className="text-6xl mb-4">👤</div>
                <h2 className="text-3xl font-bold mb-4 text-gray-900">
                  Almost Ready!
                </h2>
                <p className="text-lg text-gray-700 mb-6">
                  You&apos;re making progress! Add a few more contacts to start practicing.
                </p>

                <p className="text-lg text-amber-700 mb-6">
                  You currently have {formatEntrySummary()}.
                  Add {(status?.min_contacts_required || 2) - (status?.total_count || 0)} more to begin!
                </p>

                <div className="bg-white rounded-lg p-6 mb-6 text-left">
                  <h3 className="text-2xl font-bold mb-4 text-gray-900">
                    What you&apos;ll add:
                  </h3>
                  <ul className="space-y-3 text-lg text-gray-700">
                    <li className="flex items-start">
                      <span className="text-[var(--color-primary)] mr-3 text-2xl">1.</span>
                      <span>A clear photo of the person or item</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-[var(--color-primary)] mr-3 text-2xl">2.</span>
                      <span>Their name and any nicknames you use</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-[var(--color-primary)] mr-3 text-2xl">3.</span>
                      <span>Your relationship (wife, grandson, friend, pet, etc.)</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-[var(--color-primary)] mr-3 text-2xl">4.</span>
                      <span>Optional: A description or association to help you remember</span>
                    </li>
                  </ul>
                </div>

                <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center flex-wrap">
                  <Link
                    href="/dashboard/treatments/life-words/setup"
                    className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold py-6 px-12 rounded-lg text-2xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2 inline-block text-center"
                    style={{ minHeight: '44px' }}
                  >
                    Add More Contacts
                  </Link>

                  <Link
                    href="/dashboard/treatments/life-words/how-it-works"
                    className="bg-blue-50 hover:bg-blue-100 text-blue-700 font-bold py-6 px-8 rounded-lg text-xl transition-colors focus:outline-none focus:ring-4 focus:ring-blue-300 focus:ring-offset-2 inline-block text-center"
                    style={{ minHeight: '44px' }}
                  >
                    How It Works
                  </Link>

                  <Link
                    href="/dashboard/treatments/life-words/messages"
                    className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold py-6 px-8 rounded-lg text-xl transition-colors focus:outline-none focus:ring-4 focus:ring-gray-300 focus:ring-offset-2 inline-flex items-center justify-center gap-2"
                    style={{ minHeight: '44px' }}
                  >
                    Messages
                    <UnreadBadge />
                  </Link>
                </div>
              </>
            )}
          </div>
        ) : (
          // Ready to practice - user has enough contacts
          <div className="bg-green-50 border-2 border-green-200 rounded-lg p-8 mb-6">
            <div className="text-6xl mb-4">🎯</div>
            <h2 className="text-3xl font-bold mb-4 text-gray-900">
              Ready to Practice!
            </h2>
            <p className="text-lg text-gray-700 mb-6">
              You have {formatEntrySummary()} ready.
              Start a session to practice naming them!
            </p>

            {error && (
              <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 mb-6">
                <p className="text-red-700 text-lg font-semibold">Error: {error}</p>
              </div>
            )}

            {/* Category Choice Dialog */}
            {showCategoryChoice && (
              <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 mb-6">
                <h3 className="text-2xl font-bold mb-4 text-gray-900 text-center">
                  What would you like to practice?
                </h3>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <button
                    onClick={() => startSessionWithCategory('people')}
                    disabled={isStarting}
                    className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] disabled:bg-gray-400 text-white font-bold py-6 px-12 rounded-lg text-2xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                    style={{ minHeight: '44px' }}
                  >
                    People ({status?.contact_count})
                  </button>
                  <button
                    onClick={() => startSessionWithCategory('items')}
                    disabled={isStarting}
                    className="bg-orange-500 hover:bg-orange-600 disabled:bg-gray-400 text-white font-bold py-6 px-12 rounded-lg text-2xl transition-colors focus:outline-none focus:ring-4 focus:ring-orange-300 focus:ring-offset-2"
                    style={{ minHeight: '44px' }}
                  >
                    Stuff ({status?.item_count})
                  </button>
                </div>
                <button
                  onClick={() => setShowCategoryChoice(false)}
                  className="mt-4 text-gray-500 hover:text-gray-700 text-lg underline mx-auto block"
                >
                  Cancel
                </button>
              </div>
            )}

            {/* Subscription gate */}
            {!canPractice && (
              <div className="bg-amber-50 border-2 border-amber-200 rounded-lg p-4 mb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <p className="text-amber-800 text-lg font-semibold">
                  Subscribe to start practicing
                </p>
                <Link
                  href="/pricing"
                  className="bg-amber-600 hover:bg-amber-700 text-white font-semibold py-3 px-6 rounded-lg text-lg transition-colors whitespace-nowrap"
                  style={{ minHeight: '44px' }}
                >
                  View Plans
                </Link>
              </div>
            )}

            {/* Primary Practice Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center flex-wrap">
              <button
                onClick={handleStartSession}
                disabled={isStarting || !canPractice}
                className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-bold py-6 px-12 rounded-lg text-2xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                style={{ minHeight: '44px' }}
              >
                {isStarting ? 'Starting...' : 'Name Practice'}
              </button>

              <button
                onClick={handleStartQuestionSession}
                disabled={isStarting || !canPractice}
                className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-bold py-6 px-12 rounded-lg text-2xl transition-colors focus:outline-none focus:ring-4 focus:ring-purple-300 focus:ring-offset-2"
                style={{ minHeight: '44px' }}
              >
                {isStarting ? 'Starting...' : 'Question Practice'}
              </button>

              <button
                onClick={handleStartInformationSession}
                disabled={isStarting || !canPractice || !infoStatus?.can_start_session}
                title={!canPractice ? 'Subscribe to access practice sessions' : !infoStatus?.can_start_session ? `Fill in at least ${infoStatus?.min_fields_required || 5} fields in "My Info" to practice` : 'Practice recalling your personal information'}
                className="bg-teal-600 hover:bg-teal-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-bold py-6 px-12 rounded-lg text-2xl transition-colors focus:outline-none focus:ring-4 focus:ring-teal-300 focus:ring-offset-2"
                style={{ minHeight: '44px' }}
              >
                {isStarting ? 'Starting...' : 'Information Practice'}
              </button>
            </div>

            {/* Information Practice Helper Text */}
            {!infoStatus?.can_start_session && infoStatus && (
              <div className="mt-4 text-center">
                <p className="text-gray-600 text-base">
                  <span className="text-teal-600 font-semibold">Information Practice:</span> Fill in at least {infoStatus.min_fields_required} fields in{' '}
                  <Link href="/dashboard/treatments/life-words/my-information" className="text-teal-600 underline hover:text-teal-700">
                    My Info
                  </Link>{' '}
                  to enable. ({infoStatus.filled_fields_count}/{infoStatus.min_fields_required} filled)
                </p>
              </div>
            )}

            {/* Secondary Actions - Icon Grid */}
            <div className="mt-8 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-8 gap-3">
              <Link
                href="/dashboard/treatments/life-words/quick-add"
                title="Quickly add photos of people and things"
                className="flex flex-col items-center justify-center p-3 rounded-lg bg-white hover:bg-blue-50 border-2 border-gray-200 hover:border-blue-300 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-300 min-h-[90px]"
              >
                <span className="text-2xl mb-1">📸</span>
                <span className="text-xs sm:text-sm font-semibold text-gray-700 text-center leading-tight">Quick Add</span>
              </Link>

              <Link
                href="/dashboard/treatments/life-words/how-it-works"
                title="Learn how to use this feature"
                className="flex flex-col items-center justify-center p-3 rounded-lg bg-white hover:bg-blue-50 border-2 border-gray-200 hover:border-blue-300 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-300 min-h-[90px]"
              >
                <span className="text-2xl mb-1">❓</span>
                <span className="text-xs sm:text-sm font-semibold text-gray-700 text-center leading-tight">Instructions</span>
              </Link>

              <Link
                href="/dashboard/treatments/life-words/progress"
                title="View your progress and statistics"
                className="flex flex-col items-center justify-center p-3 rounded-lg bg-white hover:bg-green-50 border-2 border-gray-200 hover:border-green-300 transition-colors focus:outline-none focus:ring-2 focus:ring-green-300 min-h-[90px]"
              >
                <span className="text-2xl mb-1">📊</span>
                <span className="text-xs sm:text-sm font-semibold text-gray-700 text-center leading-tight">Progress</span>
              </Link>

              <Link
                href="/dashboard/treatments/life-words/messages"
                title="View messages from family and caregivers"
                className="flex flex-col items-center justify-center p-3 rounded-lg bg-white hover:bg-blue-50 border-2 border-gray-200 hover:border-blue-300 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-300 min-h-[90px]"
              >
                <span className="text-2xl mb-1">💬</span>
                <span className="text-xs sm:text-sm font-semibold text-gray-700 text-center leading-tight">Messages</span>
                <UnreadBadge />
              </Link>

              <Link
                href="/dashboard/treatments/life-words/contacts"
                title="Add or edit your contacts"
                className="flex flex-col items-center justify-center p-3 rounded-lg bg-white hover:bg-gray-50 border-2 border-gray-200 hover:border-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-300 min-h-[90px]"
              >
                <span className="text-2xl mb-1">👥</span>
                <span className="text-xs sm:text-sm font-semibold text-gray-700 text-center leading-tight">My People</span>
              </Link>

              <Link
                href="/dashboard/treatments/life-words/my-information"
                title="Update your personal information"
                className="flex flex-col items-center justify-center p-3 rounded-lg bg-white hover:bg-gray-50 border-2 border-gray-200 hover:border-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-300 min-h-[90px]"
              >
                <span className="text-2xl mb-1">ℹ️</span>
                <span className="text-xs sm:text-sm font-semibold text-gray-700 text-center leading-tight">My Info</span>
              </Link>

              <Link
                href="/dashboard/treatments/life-words/items"
                title="Manage your items and belongings"
                className="flex flex-col items-center justify-center p-3 rounded-lg bg-white hover:bg-gray-50 border-2 border-gray-200 hover:border-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-300 min-h-[90px]"
              >
                <span className="text-2xl mb-1">📦</span>
                <span className="text-xs sm:text-sm font-semibold text-gray-700 text-center leading-tight">My Stuff</span>
              </Link>

              <Link
                href="/dashboard/settings"
                title="Adjust voice and answer matching settings"
                className="flex flex-col items-center justify-center p-3 rounded-lg bg-white hover:bg-gray-50 border-2 border-gray-200 hover:border-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-300 min-h-[90px]"
              >
                <span className="text-2xl mb-1">⚙️</span>
                <span className="text-xs sm:text-sm font-semibold text-gray-700 text-center leading-tight">Settings</span>
              </Link>
            </div>
          </div>
        )}

        <div className="mt-6 text-center">
          <Link
            href="/dashboard"
            className="inline-block text-[var(--color-primary)] hover:underline text-lg"
          >
            ← Back to Dashboard
          </Link>
        </div>

        <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-6 mt-6">
          <h3 className="text-2xl font-bold mb-3 text-gray-900">
            Why personalized practice?
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-base text-gray-700">
            <div className="flex items-start">
              <span className="text-green-600 mr-2">✓</span>
              <span>Practice with familiar faces and items</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 mr-2">✓</span>
              <span>Personalized cues based on your relationships</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 mr-2">✓</span>
              <span>More meaningful and motivating practice</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 mr-2">✓</span>
              <span>Progress tracking for each person/item</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
