'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams } from 'next/navigation'
import { apiClient, ApiError } from '@/lib/api/client'
import { MessageList } from '@/components/messaging/MessageList'
import { MessageInput } from '@/components/messaging/MessageInput'
import { ShareLinkModal } from '@/components/messaging/ShareLinkModal'
import Image from 'next/image'
import Link from 'next/link'

interface Message {
  id: string
  direction: string
  text_content: string | null
  photo_url: string | null
  voice_url: string | null
  voice_duration_seconds: number | null
  is_read: boolean
  created_at: string
}

interface Contact {
  id: string
  name: string
  photo_url: string
  relationship: string
}

export default function ConversationPage() {
  const params = useParams()
  const contactId = params.contactId as string

  const [messages, setMessages] = useState<Message[]>([])
  const [contact, setContact] = useState<Contact | null>(null)
  const [messagingUrl, setMessagingUrl] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSending, setIsSending] = useState(false)
  const [showShareModal, setShowShareModal] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadConversation()
    loadMessagingToken()
    // Poll for new messages every 10 seconds
    const interval = setInterval(loadConversation, 10000)
    return () => clearInterval(interval)
  }, [contactId])

  useEffect(() => {
    // Scroll to bottom when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadConversation = async () => {
    try {
      const data = await apiClient.get<any>(`/api/life-words/messaging/conversations/${contactId}`)
      setMessages(data.messages)
      setContact(data.contact)

      // Mark messages as read
      await apiClient.put(`/api/life-words/messaging/conversations/${contactId}/read`)
    } catch (err: any) {
      if (err instanceof ApiError && err.status === 404) {
        setError('Contact not found')
      } else {
        setError(err.message || 'An error occurred')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const loadMessagingToken = async () => {
    try {
      const data = await apiClient.get<any>(`/api/life-words/messaging/conversations/${contactId}/token`)
      setMessagingUrl(data.messaging_url)
    } catch (err) {
      console.error('Error loading messaging token:', err)
    }
  }

  const handleSendMessage = async (content: {
    text_content?: string
    photo_url?: string
    voice_url?: string
    voice_duration_seconds?: number
  }) => {
    setIsSending(true)
    try {
      const newMessage = await apiClient.post<Message>(
        `/api/life-words/messaging/conversations/${contactId}/messages`,
        content
      )
      setMessages(prev => [...prev, newMessage])
    } catch (err) {
      console.error('Error sending message:', err)
      alert('Failed to send message')
    } finally {
      setIsSending(false)
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

  if (error || !contact) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8">
        <div className="text-center py-12">
          <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-xl text-gray-600 mb-4">{error || 'Contact not found'}</p>
          <Link
            href="/dashboard/treatments/life-words/messages"
            className="text-blue-500 hover:underline"
          >
            ← Back to Messages
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="h-[calc(100vh-180px)] flex flex-col bg-white rounded-lg shadow-md overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-white">
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard/treatments/life-words/messages"
            className="p-1 hover:bg-gray-100 rounded-full"
          >
            <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Link>
          <div className="relative w-10 h-10 rounded-full overflow-hidden">
            <Image
              src={contact.photo_url}
              alt={contact.name}
              fill
              className="object-cover"
            />
          </div>
          <div>
            <h2 className="font-bold text-gray-900">{contact.name}</h2>
            <p className="text-sm text-gray-500">{contact.relationship}</p>
          </div>
        </div>
        <button
          onClick={() => setShowShareModal(true)}
          className="px-4 py-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 font-semibold text-sm"
        >
          Share Link
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        <MessageList messages={messages} isLoading={false} userPerspective={true} />
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <MessageInput onSend={handleSendMessage} isSending={isSending} isPublic={false} />

      {/* Share Modal */}
      <ShareLinkModal
        isOpen={showShareModal}
        onClose={() => setShowShareModal(false)}
        messagingUrl={messagingUrl}
        contactName={contact.name}
      />
    </div>
  )
}
