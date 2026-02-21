'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [user, setUser] = useState<import('@supabase/supabase-js').User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const supabase = createClient()

  useEffect(() => {
    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      setUser(user)
      setLoading(false)
    }

    getUser()
  }, [supabase.auth])

  const handleLogout = async () => {
    await supabase.auth.signOut()
    router.push('/login')
    router.refresh()
  }

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
                alt="Parrot Software Logo"
                width={50}
                height={50}
                className="object-contain flex-shrink-0 w-10 h-10 sm:w-[50px] sm:h-[50px]"
              />
              <div className="text-xl sm:text-3xl font-bold text-[var(--color-primary)] truncate">
                Parrot Software
              </div>
            </Link>

            <div className="flex items-center space-x-2 sm:space-x-4 min-w-0">
              <span className="hidden sm:inline text-lg text-gray-700 truncate max-w-[150px] md:max-w-none">
                {user?.email}
              </span>
              <button
                onClick={handleLogout}
                className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-semibold py-2 sm:py-3 px-4 sm:px-6 rounded-lg text-base sm:text-lg transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2 flex-shrink-0"
                style={{ minHeight: '44px' }}
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <main id="main-content">
          {children}
        </main>
      </div>
    </div>
  )
}
