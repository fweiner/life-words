'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase'
import Link from 'next/link'

export default function DashboardPage() {
  const [user, setUser] = useState<import('@supabase/supabase-js').User | null>(null)
  const supabase = createClient()

  useEffect(() => {
    const loadUserData = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      setUser(user)
    }

    loadUserData()
  }, [supabase.auth])

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <h1 className="text-4xl font-bold mb-4 text-[var(--color-primary)]">
          Welcome back{user?.user_metadata?.full_name ? `, ${user.user_metadata.full_name}` : ''}!
        </h1>
        <p className="text-xl text-gray-700">
          Ready to continue your recovery journey?
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="grid grid-cols-1 gap-6">
          {/* My Life Words and Memory - Active */}
          <div className="p-6 border-2 border-[var(--color-primary)] rounded-lg">
            <div className="flex items-start space-x-4">
              <div className="text-5xl">👤</div>
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-[var(--color-primary)] mb-2">
                  My Life Words and Memory
                </h3>
                <p className="text-lg text-gray-700 mb-3">
                  Practice naming the people, pets, and things that matter most to you.
                </p>
                <div className="flex flex-wrap gap-3 mt-1">
                  <Link
                    href="/dashboard/practice/preparation"
                    className="inline-block border-2 border-[var(--color-primary)] text-[var(--color-primary)] px-4 py-2 rounded-full text-base font-semibold hover:bg-blue-50 transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                  >
                    Preparation
                  </Link>
                  <Link
                    href="/dashboard/practice"
                    className="inline-block bg-[var(--color-primary)] text-white px-4 py-2 rounded-full text-base font-semibold hover:bg-[var(--color-primary-hover)] transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
                  >
                    Start Now →
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
