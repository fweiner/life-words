'use client'

import { useEffect, useState } from 'react'
import { apiClient } from '@/lib/api/client'

interface ProgressData {
  id: string
  treatment_type: string
  total_sessions: number
  average_score: number | null
  last_session_at: string | null
  updated_at: string
}

interface SessionData {
  id: string
  treatment_type: string
  started_at: string
  completed_at: string | null
  created_at: string
}

export default function ProgressPage() {
  const [progress, setProgress] = useState<ProgressData[]>([])
  const [recentSessions, setRecentSessions] = useState<SessionData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadProgress = async () => {
      try {
        // Fetch progress data
        try {
          const progressData = await apiClient.get<ProgressData[]>('/api/results/my-progress')
          setProgress(progressData)
        } catch {
          // silently handle progress fetch failure
        }

        // Fetch recent sessions
        try {
          const sessionsData = await apiClient.get<SessionData[]>('/api/treatments/sessions?limit=10')
          setRecentSessions(sessionsData)
        } catch {
          // silently handle sessions fetch failure
        }

      } catch (error) {
        console.error('Failed to load progress:', error)
      } finally {
        setLoading(false)
      }
    }

    loadProgress()
  }, [])

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getTreatmentName = (type: string) => {
    const names: { [key: string]: string } = {
      'speech_echo': '🎤 Speech Echo',
      'word_finding': '📝 Word Finding',
      'short_term_memory': '🧠 Short Term Memory'
    }
    return names[type] || type
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-2xl">Loading your progress...</div>
      </div>
    )
  }

  const totalSessions = progress.reduce((sum, p) => sum + p.total_sessions, 0)

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <h1 className="text-4xl font-bold mb-4 text-[var(--color-primary)]">
          📊 My Progress
        </h1>
        <p className="text-xl text-gray-700">
          Track your cognitive therapy journey and see how far you've come.
        </p>
      </div>

      {/* Overall Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-[var(--color-primary)]">
          <div className="text-5xl mb-3">🎯</div>
          <div className="text-4xl font-bold text-[var(--color-primary)] mb-2">
            {totalSessions}
          </div>
          <div className="text-xl text-gray-600">Total Sessions Completed</div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-[var(--color-accent)]">
          <div className="text-5xl mb-3">📚</div>
          <div className="text-4xl font-bold text-[var(--color-accent)] mb-2">
            {progress.length}
          </div>
          <div className="text-xl text-gray-600">Activities Tried</div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-[var(--color-success)]">
          <div className="text-5xl mb-3">⭐</div>
          <div className="text-4xl font-bold text-[var(--color-success)] mb-2">
            {totalSessions > 0 ? 'Great!' : 'Start!'}
          </div>
          <div className="text-xl text-gray-600">
            {totalSessions > 0 ? 'Keep up the good work' : 'Begin your journey'}
          </div>
        </div>
      </div>

      {/* Progress by Treatment Type */}
      {progress.length > 0 ? (
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-3xl font-bold mb-6">Progress by Activity</h2>

          <div className="space-y-6">
            {progress.map((item) => (
              <div key={item.id} className="border-2 border-gray-200 rounded-lg p-6">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold mb-3">
                      {getTreatmentName(item.treatment_type)}
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-lg">
                      <div>
                        <span className="font-semibold">Sessions:</span>
                        <span className="ml-2 text-[var(--color-primary)] font-bold">
                          {item.total_sessions}
                        </span>
                      </div>

                      {item.average_score !== null && (
                        <div>
                          <span className="font-semibold">Avg Score:</span>
                          <span className="ml-2 text-[var(--color-accent)] font-bold">
                            {Math.round(item.average_score)}%
                          </span>
                        </div>
                      )}

                      <div>
                        <span className="font-semibold">Last Session:</span>
                        <span className="ml-2 text-gray-600">
                          {item.last_session_at
                            ? new Date(item.last_session_at).toLocaleDateString()
                            : 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-8 text-center">
          <div className="text-6xl mb-4">🎯</div>
          <h2 className="text-2xl font-bold mb-3 text-[var(--color-primary)]">
            No sessions yet
          </h2>
          <p className="text-xl text-gray-700 mb-6">
            Start your first treatment to see your progress here!
          </p>
          <a
            href="/dashboard/treatments/speech-echo"
            className="inline-block bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold py-4 px-8 rounded-lg text-xl transition-colors focus:outline-none focus:ring-4 focus:ring-[var(--color-primary)] focus:ring-offset-2"
          >
            Try Speech Echo →
          </a>
        </div>
      )}

      {/* Recent Activity */}
      {recentSessions.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-3xl font-bold mb-6">Recent Sessions</h2>

          <div className="overflow-x-auto">
            <table className="w-full text-lg">
              <thead>
                <tr className="border-b-2 border-gray-200">
                  <th className="text-left py-4 px-4 font-bold">Activity</th>
                  <th className="text-left py-4 px-4 font-bold">Date</th>
                  <th className="text-left py-4 px-4 font-bold">Status</th>
                </tr>
              </thead>
              <tbody>
                {recentSessions.map((session) => (
                  <tr key={session.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-4 px-4">
                      {getTreatmentName(session.treatment_type)}
                    </td>
                    <td className="py-4 px-4 text-gray-600">
                      {formatDate(session.started_at)}
                    </td>
                    <td className="py-4 px-4">
                      {session.completed_at ? (
                        <span className="inline-block bg-green-100 text-green-800 px-3 py-1 rounded-full font-semibold">
                          ✓ Completed
                        </span>
                      ) : (
                        <span className="inline-block bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full font-semibold">
                          ⏳ In Progress
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
