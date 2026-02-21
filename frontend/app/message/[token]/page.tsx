'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams } from 'next/navigation'
import { apiClient } from '@/lib/api/client'
import { MessageList } from '@/components/messaging/MessageList'
import { MessageInput } from '@/components/messaging/MessageInput'
import Image from 'next/image'

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

interface TokenStatus {
  valid: boolean
  status: 'active' | 'inactive' | 'not_found'
  user_name?: string
  contact_name?: string
  contact_photo_url?: string
}

export default function PublicMessagePage() {
  const params = useParams()
  const token = params.token as string

  const [tokenStatus, setTokenStatus] = useState<TokenStatus | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSending, setIsSending] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const verifyToken = useCallback(async () => {
    try {
      const data = await apiClient.getPublic<TokenStatus>(
        `/api/life-words/messaging/public/verify/${token}`
      )
      setTokenStatus(data)
    } catch (err: unknown) {
      console.error('Error verifying token:', err)
      setTokenStatus({
        valid: false,
        status: 'not_found'
      })
    } finally {
      setIsLoading(false)
    }
  }, [token])

  const loadMessages = useCallback(async () => {
    try {
      const data = await apiClient.getPublic<Message[]>(
        `/api/life-words/messaging/public/${token}/messages`
      )
      setMessages(data)
    } catch (err: unknown) {
      console.error('Error loading messages:', err)
    }
  }, [token])

  useEffect(() => {
    verifyToken()
  }, [verifyToken])

  useEffect(() => {
    if (tokenStatus?.valid) {
      loadMessages()
      const interval = setInterval(loadMessages, 10000)
      return () => clearInterval(interval)
    }
  }, [tokenStatus?.valid, loadMessages])

  const handleSendMessage = async (content: {
    text_content?: string
    photo_url?: string
    voice_url?: string
    voice_duration_seconds?: number
  }) => {
    setIsSending(true)
    try {
      const newMessage = await apiClient.postPublic<Message>(
        `/api/life-words/messaging/public/${token}/messages`,
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

  // Not found
  if (!tokenStatus || tokenStatus.status === 'not_found') {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-6xl mb-4">&#x1F50D;</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Link Not Found</h2>
        <p className="text-lg text-gray-600">
          This messaging link doesn&apos;t exist or may have been removed.
          Please check with the person who sent you this link.
        </p>
      </div>
    )
  }

  // Inactive
  if (tokenStatus.status === 'inactive') {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-6xl mb-4">&#x1F6AB;</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Link Disabled</h2>
        <p className="text-lg text-gray-600">
          This messaging link has been disabled. Please contact{' '}
          {tokenStatus.user_name || 'the person who sent you this link'}{' '}
          for a new link.
        </p>
      </div>
    )
  }

  // Valid token - show messaging interface
  const userFirstName = tokenStatus.user_name?.split(' ')[0] || 'them'

  return (
    <div className="h-[calc(100vh-200px)] flex flex-col bg-white rounded-lg shadow-md overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-3 p-4 border-b bg-white">
        {tokenStatus.contact_photo_url && (
          <div className="relative w-10 h-10 rounded-full overflow-hidden">
            <Image
              src={tokenStatus.contact_photo_url}
              alt={tokenStatus.contact_name || 'You'}
              fill
              className="object-cover"
            />
          </div>
        )}
        <div>
          <p className="text-sm text-gray-500">Messaging with</p>
          <h2 className="font-bold text-gray-900">{tokenStatus.user_name || 'User'}</h2>
        </div>
      </div>

      {/* Welcome message if no messages */}
      {messages.length === 0 && (
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center max-w-md">
            <div className="text-6xl mb-4">&#x1F44B;</div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Start a Conversation
            </h3>
            <p className="text-gray-600">
              Send a message to {userFirstName}. Your messages will help them
              practice communication skills as part of their memory rehabilitation.
            </p>
            <div className="mt-4 p-4 bg-blue-50 rounded-lg text-left">
              <p className="text-blue-800 text-sm">
                <strong>Tip:</strong> You can send text messages, photos, or voice recordings.
                Keep messages friendly and supportive!
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Messages */}
      {messages.length > 0 && (
        <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
          <MessageList messages={messages} isLoading={false} userPerspective={false} />
          <div ref={messagesEndRef} />
        </div>
      )}

      {/* Input */}
      <MessageInput onSend={handleSendMessage} isSending={isSending} isPublic={true} />
    </div>
  )
}
