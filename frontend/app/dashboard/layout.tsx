'use client'

import { useEffect, useState, useRef } from 'react'
import { createClient } from '@/lib/supabase'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'
import { useSubscription } from '@/lib/hooks/useSubscription'
import { TrialBanner } from '@/components/subscription/TrialBanner'
import { apiClient } from '@/lib/api/client'

const ADMIN_EMAIL = 'weiner@parrotsoftware.com'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [user, setUser] = useState<import('@supabase/supabase-js').User | null>(null)
  const [loading, setLoading] = useState(true)
  const [menuOpen, setMenuOpen] = useState(false)
  const [voiceGender, setVoiceGender] = useState<'male' | 'female'>('female')
  const [voiceOpen, setVoiceOpen] = useState(false)
  const voiceRef = useRef<HTMLDivElement>(null)
  const router = useRouter()
  const supabase = createClient()
  const { subscription } = useSubscription()

  useEffect(() => {
    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      setUser(user)
      setLoading(false)
    }

    getUser()
  }, [supabase.auth])

  useEffect(() => {
    async function loadVoicePreference() {
      try {
        const profile = await apiClient.get<Record<string, unknown>>('/api/profile')
        const gender = profile.voice_gender as string
        if (gender === 'male' || gender === 'female') {
          setVoiceGender(gender)
        }
      } catch {
        // Use default
      }
    }
    loadVoicePreference()
  }, [])

  // Close voice dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (voiceRef.current && !voiceRef.current.contains(e.target as Node)) {
        setVoiceOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleVoiceChange = async (gender: 'male' | 'female') => {
    setVoiceGender(gender)
    setVoiceOpen(false)
    try {
      await apiClient.patch('/api/profile', { voice_gender: gender })
    } catch {
      // Revert on error could be added, but voice is not critical
    }
  }

  const handleLogout = async () => {
    await supabase.auth.signOut()
    router.push('/login')
    router.refresh()
  }

  const displayName = user?.user_metadata?.full_name || user?.email || ''
  const isAdmin = user?.email === ADMIN_EMAIL

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-2xl">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[var(--color-background)]">
      {/* Header */}
      <header className="bg-white border-b-2 border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <Link href="/dashboard" className="flex items-center space-x-2 sm:space-x-3 min-w-0">
              <Image
                src="/header.jpg"
                alt="Life Words Logo"
                width={50}
                height={50}
                className="object-contain flex-shrink-0 w-10 h-10 sm:w-[50px] sm:h-[50px]"
              />
              <div className="text-xl sm:text-3xl font-bold text-[var(--color-primary)] truncate">
                Life Words
              </div>
            </Link>

            <nav className="flex items-center space-x-1 sm:space-x-4 min-w-0">
              {/* Desktop nav */}
              {isAdmin && (
                <Link
                  href="/dashboard/admin"
                  className="hidden md:inline text-base text-gray-700 hover:text-[var(--color-primary)] transition-colors px-2 py-1"
                >
                  Administrator
                </Link>
              )}
              <Link
                href="/dashboard/account"
                className="hidden md:inline text-base text-gray-700 hover:text-[var(--color-primary)] transition-colors px-2 py-1"
              >
                Manage My Account
              </Link>

              {/* Voice dropdown (desktop) */}
              <div ref={voiceRef} className="relative hidden md:block">
                <button
                  onClick={() => setVoiceOpen(!voiceOpen)}
                  className="flex items-center text-base text-gray-700 hover:text-[var(--color-primary)] transition-colors px-2 py-1"
                  style={{ minHeight: '44px' }}
                >
                  Voice: {voiceGender === 'female' ? 'Female' : 'Male'}
                  <svg className="ml-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={voiceOpen ? 'M5 15l7-7 7 7' : 'M19 9l-7 7-7-7'} />
                  </svg>
                </button>
                {voiceOpen && (
                  <div className="absolute right-0 mt-1 w-40 bg-white border border-gray-200 rounded-lg shadow-lg z-20">
                    <button
                      onClick={() => handleVoiceChange('female')}
                      className={`w-full text-left px-4 py-3 text-base hover:bg-gray-50 rounded-t-lg ${voiceGender === 'female' ? 'font-semibold text-[var(--color-primary)]' : 'text-gray-700'}`}
                      style={{ minHeight: '44px' }}
                    >
                      Female
                    </button>
                    <button
                      onClick={() => handleVoiceChange('male')}
                      className={`w-full text-left px-4 py-3 text-base hover:bg-gray-50 rounded-b-lg ${voiceGender === 'male' ? 'font-semibold text-[var(--color-primary)]' : 'text-gray-700'}`}
                      style={{ minHeight: '44px' }}
                    >
                      Male
                    </button>
                  </div>
                )}
              </div>

              <span className="hidden lg:inline text-base text-gray-500 truncate max-w-[200px]">
                {displayName}
              </span>
              <button
                onClick={handleLogout}
                className="hidden md:inline text-base text-gray-700 hover:text-[var(--color-primary)] transition-colors px-2 py-1"
                style={{ minHeight: '44px' }}
              >
                Sign Out
              </button>

              {/* Mobile hamburger button */}
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="md:hidden flex items-center justify-center w-11 h-11 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                aria-label={menuOpen ? 'Close menu' : 'Open menu'}
              >
                {menuOpen ? (
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                ) : (
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="3" y1="6" x2="21" y2="6" />
                    <line x1="3" y1="12" x2="21" y2="12" />
                    <line x1="3" y1="18" x2="21" y2="18" />
                  </svg>
                )}
              </button>
            </nav>
          </div>

          {/* Mobile dropdown menu */}
          {menuOpen && (
            <div className="md:hidden border-t border-gray-200 pb-4">
              <div className="flex flex-col space-y-1 px-4 pt-3">
                {isAdmin && (
                  <Link
                    href="/dashboard/admin"
                    onClick={() => setMenuOpen(false)}
                    className="text-lg text-gray-700 hover:text-[var(--color-primary)] hover:bg-gray-50 transition-colors px-3 py-3 rounded-lg"
                    style={{ minHeight: '44px' }}
                  >
                    Administrator
                  </Link>
                )}
                <Link
                  href="/dashboard/account"
                  onClick={() => setMenuOpen(false)}
                  className="text-lg text-gray-700 hover:text-[var(--color-primary)] hover:bg-gray-50 transition-colors px-3 py-3 rounded-lg"
                  style={{ minHeight: '44px' }}
                >
                  Manage My Account
                </Link>

                {/* Voice selector (mobile) */}
                <div className="px-3 py-3">
                  <div className="text-base font-medium text-gray-700 mb-2">Voice</div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleVoiceChange('female')}
                      className={`flex-1 py-3 px-4 rounded-lg text-base font-medium border-2 transition-colors ${
                        voiceGender === 'female'
                          ? 'border-[var(--color-primary)] bg-blue-50 text-[var(--color-primary)]'
                          : 'border-gray-300 text-gray-700 hover:border-gray-400'
                      }`}
                      style={{ minHeight: '44px' }}
                    >
                      Female
                    </button>
                    <button
                      onClick={() => handleVoiceChange('male')}
                      className={`flex-1 py-3 px-4 rounded-lg text-base font-medium border-2 transition-colors ${
                        voiceGender === 'male'
                          ? 'border-[var(--color-primary)] bg-blue-50 text-[var(--color-primary)]'
                          : 'border-gray-300 text-gray-700 hover:border-gray-400'
                      }`}
                      style={{ minHeight: '44px' }}
                    >
                      Male
                    </button>
                  </div>
                </div>

                {displayName && (
                  <span className="text-base text-gray-500 px-3 py-2">
                    {displayName}
                  </span>
                )}
                <button
                  onClick={() => { setMenuOpen(false); handleLogout() }}
                  className="text-left text-lg text-red-600 hover:bg-red-50 transition-colors px-3 py-3 rounded-lg font-semibold"
                  style={{ minHeight: '44px' }}
                >
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {subscription && !subscription.is_paid && (
          <TrialBanner
            accountStatus={subscription.account_status}
            trialEndsAt={subscription.trial_ends_at}
            isTrialActive={subscription.is_trial_active}
            isPaid={subscription.is_paid}
            canPractice={subscription.can_practice}
            hasSubscription={subscription.has_subscription}
          />
        )}
        <main id="main-content">
          {children}
        </main>
      </div>
    </div>
  )
}
