'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api/client'
import Link from 'next/link'
import Image from 'next/image'

interface ConversationSummary {
  contact_id: string
  contact_name: string
  contact_photo_url: string
  contact_relationship: string
  last_message_text: string | null
  last_message_at: string | null
  last_message_direction: string | null
  unread_count: number
  has_messaging_token: boolean
}

export default function MessagesInboxPage() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadConversations()
    // Poll for new messages every 30 seconds
    const interval = setInterval(loadConversations, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadConversations = async () => {
    try {
      const data = await apiClient.get<ConversationSummary[]>('/api/life-words/messaging/conversations')
      setConversations(data)
    } catch (err: unknown) {
      const e = err as Record<string, unknown>
      setError((e.message as string) || 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  const formatTime = (dateStr: string | null) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const now = new Date()
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))

    if (diffDays === 0) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } else if (diffDays === 1) {
      return 'Yesterday'
    } else if (diffDays < 7) {
      return date.toLocaleDateString([], { weekday: 'short' })
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
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

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Messages</h1>
            <p className="text-lg text-gray-600 mt-1">
              Conversations with your contacts
            </p>
          </div>
          <Link
            href="/dashboard/treatments/life-words"
            className="text-[var(--color-primary)] hover:underline"
          >
            ← Back
          </Link>
        </div>

        {error && (
          <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 mb-6">
            <p className="text-red-700 font-semibold">{error}</p>
          </div>
        )}

        {conversations.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <p className="text-xl text-gray-600 mb-2">No conversations yet</p>
            <p className="text-gray-500 mb-4">Add contacts and share messaging links to start conversations</p>
            <Link
              href="/dashboard/treatments/life-words/contacts"
              className="inline-block px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              Manage Contacts
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {conversations.map((conv) => (
              <Link
                key={conv.contact_id}
                href={`/dashboard/treatments/life-words/messages/${conv.contact_id}`}
                className="flex items-center gap-4 p-4 hover:bg-gray-50 transition-colors rounded-lg -mx-4"
              >
                {/* Contact photo */}
                <div className="relative flex-shrink-0">
                  <div className="relative w-14 h-14 rounded-full overflow-hidden">
                    <Image
                      src={conv.contact_photo_url}
                      alt={conv.contact_name}
                      fill
                      className="object-cover"
                    />
                  </div>
                  {conv.unread_count > 0 && (
                    <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
                      {conv.unread_count > 9 ? '9+' : conv.unread_count}
                    </span>
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className={`font-semibold text-gray-900 truncate ${conv.unread_count > 0 ? 'font-bold' : ''}`}>
                      {conv.contact_name}
                    </h3>
                    {conv.last_message_at && (
                      <span className={`text-sm flex-shrink-0 ml-2 ${conv.unread_count > 0 ? 'text-blue-500 font-semibold' : 'text-gray-500'}`}>
                        {formatTime(conv.last_message_at)}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500 truncate">
                    {conv.last_message_text ? (
                      <>
                        {conv.last_message_direction === 'user_to_contact' && (
                          <span className="text-gray-400">You: </span>
                        )}
                        {conv.last_message_text}
                      </>
                    ) : conv.has_messaging_token ? (
                      <span className="text-gray-400 italic">Link shared - waiting for response</span>
                    ) : (
                      <span className="text-gray-400 italic">No messages yet</span>
                    )}
                  </p>
                </div>

                {/* Arrow */}
                <svg className="w-5 h-5 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
