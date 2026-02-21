'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase'
import { apiClient } from '@/lib/api/client'
import Link from 'next/link'

interface ProgressSummary {
  total_sessions: number
  name_practice: {
    sessions: number
    correct: number
    total: number
    accuracy: number
    avg_response_time_sec: number
    avg_speech_confidence: number
  }
  question_practice: {
    sessions: number
    correct: number
    total: number
    accuracy: number
    avg_response_time_ms: number
    avg_clarity: number
  }
  information_practice: {
    sessions: number
    correct: number
    total: number
    accuracy: number
    avg_response_time_sec: number
    hint_rate: number
  }
}

interface SessionHistory {
  type: 'name' | 'question' | 'information'
  date: string
  total_correct: number
  total_incorrect?: number
  total_questions?: number
  accuracy: number
  avg_response_time?: number
  avg_cues_used?: number
  avg_clarity?: number
  hints_used?: number
}

export default function LifeWordsProgressPage() {
  const router = useRouter()
  const supabase = createClient()

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [summary, setSummary] = useState<ProgressSummary | null>(null)
  const [sessionHistory, setSessionHistory] = useState<SessionHistory[]>([])

  const loadProgress = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const { data: { user } } = await supabase.auth.getUser()
      if (!user) {
        router.push('/login')
        return
      }

      const data = await apiClient.get<Record<string, unknown>>('/api/life-words/progress')
      setSummary(data.summary as ProgressSummary)
      setSessionHistory((data.session_history as SessionHistory[]) || [])
    } catch (err: unknown) {
      console.error('Error loading progress:', err)
      const e = err as Record<string, unknown>
      setError((e?.message as string) || 'Failed to load progress')
    } finally {
      setLoading(false)
    }
  }, [supabase, router])

  useEffect(() => {
    loadProgress()
  }, [loadProgress])

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    })
  }

  const formatResponseTime = (ms: number) => {
    if (!ms || ms === 0) return 'N/A'
    if (ms < 1000) return `${Math.round(ms)}ms`
    return `${(ms / 1000).toFixed(1)}s`
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-[var(--color-primary)] mx-auto mb-4"></div>
          <p className="text-xl text-gray-700">Loading progress...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border-2 border-red-300 rounded-lg p-8">
          <h4 className="text-2xl font-bold text-red-900 mb-4">Error</h4>
          <p className="text-xl text-red-700 mb-6">{error}</p>
          <button
            onClick={() => router.push('/dashboard/treatments/life-words')}
            className="bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold py-3 px-6 rounded-lg text-lg"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  const overallAccuracy = summary
    ? Math.round(
        ((summary.name_practice.correct + summary.question_practice.correct + (summary.information_practice?.correct || 0)) /
          Math.max(1, summary.name_practice.total + summary.question_practice.total + (summary.information_practice?.total || 0))) *
          100
      )
    : 0

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <Link
          href="/dashboard/treatments/life-words"
          className="text-[var(--color-primary)] hover:underline text-lg"
        >
          &larr; Back to Life Words and Memory
        </Link>
      </div>

      <h1 className="text-3xl font-bold mb-6 text-gray-900">Your Progress</h1>

      {summary && summary.total_sessions === 0 ? (
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-8 text-center">
          <div className="text-6xl mb-4">📊</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Sessions Yet</h2>
          <p className="text-lg text-gray-700 mb-6">
            Complete some practice sessions to see your progress here!
          </p>
          <Link
            href="/dashboard/treatments/life-words"
            className="inline-block bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white font-bold py-3 px-8 rounded-lg text-lg"
          >
            Start Practicing
          </Link>
        </div>
      ) : (
        <>
          {/* Overall Stats */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-bold mb-4 text-gray-900">Overall Summary</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-blue-50 rounded-lg p-4 text-center">
                <div className="text-4xl font-bold text-blue-600">
                  {summary?.total_sessions || 0}
                </div>
                <div className="text-gray-600">Total Sessions</div>
              </div>
              <div className="bg-green-50 rounded-lg p-4 text-center">
                <div className="text-4xl font-bold text-green-600">
                  {overallAccuracy}%
                </div>
                <div className="text-gray-600">Overall Accuracy</div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4 text-center">
                <div className="text-4xl font-bold text-purple-600">
                  {(summary?.name_practice.correct || 0) + (summary?.question_practice.correct || 0) + (summary?.information_practice?.correct || 0)}
                </div>
                <div className="text-gray-600">Correct Answers</div>
              </div>
              <div className="bg-amber-50 rounded-lg p-4 text-center">
                <div className="text-4xl font-bold text-amber-600">
                  {(summary?.name_practice.total || 0) + (summary?.question_practice.total || 0) + (summary?.information_practice?.total || 0)}
                </div>
                <div className="text-gray-600">Total Attempts</div>
              </div>
            </div>
          </div>

          {/* Practice Type Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
            {/* Name Practice */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
                <span className="text-2xl mr-2">👤</span>
                Name Practice
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Sessions Completed</span>
                  <span className="font-bold text-lg">{summary?.name_practice.sessions || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Correct Answers</span>
                  <span className="font-bold text-lg text-green-600">
                    {summary?.name_practice.correct || 0}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Total Attempts</span>
                  <span className="font-bold text-lg">{summary?.name_practice.total || 0}</span>
                </div>
                <div className="pt-2 border-t">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-700 font-medium">Accuracy</span>
                    <span className="font-bold text-xl text-blue-600">
                      {summary?.name_practice.accuracy || 0}%
                    </span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-blue-600 h-3 rounded-full transition-all"
                      style={{ width: `${summary?.name_practice.accuracy || 0}%` }}
                    />
                  </div>
                </div>
                {/* Response Time */}
                <div className="pt-2 border-t">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-700 font-medium">Avg Response Time</span>
                    <span className="font-bold text-lg text-indigo-600">
                      {summary?.name_practice.avg_response_time_sec
                        ? `${summary.name_practice.avg_response_time_sec.toFixed(1)}s`
                        : 'N/A'}
                    </span>
                  </div>
                </div>
                {/* Speech Clarity */}
                <div className="pt-2 border-t">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-700 font-medium">Speech Clarity</span>
                    <span className="font-bold text-lg text-teal-600">
                      {summary?.name_practice.avg_speech_confidence
                        ? `${summary.name_practice.avg_speech_confidence}%`
                        : 'N/A'}
                    </span>
                  </div>
                  {(summary?.name_practice.avg_speech_confidence ?? 0) > 0 && (
                    <div className="bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-teal-500 h-3 rounded-full transition-all"
                        style={{ width: `${summary?.name_practice.avg_speech_confidence || 0}%` }}
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Question Practice */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
                <span className="text-2xl mr-2">❓</span>
                Question Practice
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Sessions Completed</span>
                  <span className="font-bold text-lg">{summary?.question_practice.sessions || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Correct Answers</span>
                  <span className="font-bold text-lg text-green-600">
                    {summary?.question_practice.correct || 0}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Total Questions</span>
                  <span className="font-bold text-lg">{summary?.question_practice.total || 0}</span>
                </div>
                <div className="pt-2 border-t">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-700 font-medium">Accuracy</span>
                    <span className="font-bold text-xl text-purple-600">
                      {summary?.question_practice.accuracy || 0}%
                    </span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-purple-600 h-3 rounded-full transition-all"
                      style={{ width: `${summary?.question_practice.accuracy || 0}%` }}
                    />
                  </div>
                </div>
                {/* Response Time */}
                <div className="pt-2 border-t">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-700 font-medium">Avg Response Time</span>
                    <span className="font-bold text-lg text-indigo-600">
                      {summary?.question_practice.avg_response_time_ms
                        ? formatResponseTime(summary.question_practice.avg_response_time_ms)
                        : 'N/A'}
                    </span>
                  </div>
                </div>
                {/* Speech Clarity */}
                <div className="pt-2 border-t">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-700 font-medium">Speech Clarity</span>
                    <span className="font-bold text-lg text-teal-600">
                      {summary?.question_practice.avg_clarity
                        ? `${summary.question_practice.avg_clarity}%`
                        : 'N/A'}
                    </span>
                  </div>
                  {(summary?.question_practice.avg_clarity ?? 0) > 0 && (
                    <div className="bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-teal-500 h-3 rounded-full transition-all"
                        style={{ width: `${summary?.question_practice.avg_clarity || 0}%` }}
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Information Practice */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
                <span className="text-2xl mr-2">ℹ️</span>
                Information Practice
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Sessions Completed</span>
                  <span className="font-bold text-lg">{summary?.information_practice?.sessions || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Correct Answers</span>
                  <span className="font-bold text-lg text-green-600">
                    {summary?.information_practice?.correct || 0}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Total Questions</span>
                  <span className="font-bold text-lg">{summary?.information_practice?.total || 0}</span>
                </div>
                <div className="pt-2 border-t">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-700 font-medium">Accuracy</span>
                    <span className="font-bold text-xl text-teal-600">
                      {summary?.information_practice?.accuracy || 0}%
                    </span>
                  </div>
                  <div className="bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-teal-600 h-3 rounded-full transition-all"
                      style={{ width: `${summary?.information_practice?.accuracy || 0}%` }}
                    />
                  </div>
                </div>
                {/* Response Time */}
                <div className="pt-2 border-t">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-700 font-medium">Avg Response Time</span>
                    <span className="font-bold text-lg text-indigo-600">
                      {summary?.information_practice?.avg_response_time_sec
                        ? `${summary.information_practice.avg_response_time_sec.toFixed(1)}s`
                        : 'N/A'}
                    </span>
                  </div>
                </div>
                {/* Hint Rate */}
                <div className="pt-2 border-t">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-700 font-medium">Hint Usage Rate</span>
                    <span className="font-bold text-lg text-amber-600">
                      {summary?.information_practice?.hint_rate !== undefined
                        ? `${summary.information_practice.hint_rate}%`
                        : 'N/A'}
                    </span>
                  </div>
                  {(summary?.information_practice?.hint_rate ?? 0) > 0 && (
                    <div className="bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-amber-500 h-3 rounded-full transition-all"
                        style={{ width: `${summary?.information_practice?.hint_rate || 0}%` }}
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Session History */}
          {sessionHistory.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold mb-4 text-gray-900">Recent Sessions</h3>
              <div className="space-y-3">
                {sessionHistory.map((session, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">
                        {session.type === 'name' ? '👤' : session.type === 'question' ? '❓' : 'ℹ️'}
                      </span>
                      <div>
                        <div className="font-medium text-gray-900">
                          {session.type === 'name' ? 'Name Practice' : session.type === 'question' ? 'Question Practice' : 'Information Practice'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {formatDate(session.date)}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-6">
                      {/* Response time for this session */}
                      {session.avg_response_time !== undefined && session.avg_response_time > 0 && (
                        <div className="text-center">
                          <div className="text-sm text-indigo-600 font-medium">
                            {session.type === 'name'
                              ? `${session.avg_response_time.toFixed(1)}s`
                              : formatResponseTime(session.avg_response_time)}
                          </div>
                          <div className="text-xs text-gray-400">time</div>
                        </div>
                      )}
                      {/* Clarity for question sessions */}
                      {session.type === 'question' && session.avg_clarity !== undefined && session.avg_clarity > 0 && (
                        <div className="text-center">
                          <div className="text-sm text-teal-600 font-medium">
                            {Math.round(session.avg_clarity * 100)}%
                          </div>
                          <div className="text-xs text-gray-400">clarity</div>
                        </div>
                      )}
                      <div className="text-right">
                        <div className={`text-xl font-bold ${
                          session.accuracy >= 80 ? 'text-green-600' :
                          session.accuracy >= 50 ? 'text-amber-600' : 'text-red-500'
                        }`}>
                          {session.accuracy}%
                        </div>
                        <div className="text-sm text-gray-500">
                          {session.total_correct} correct
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
