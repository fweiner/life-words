'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api/client'

interface UnreadBadgeProps {
  className?: string
}

export function UnreadBadge({ className = '' }: UnreadBadgeProps) {
  const [unreadCount, setUnreadCount] = useState(0)
  useEffect(() => {
    loadUnreadCount()
    // Poll for new messages every 30 seconds
    const interval = setInterval(loadUnreadCount, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadUnreadCount = async () => {
    try {
      const data = await apiClient.get<{ count: number }>(
        '/api/life-words/messaging/unread-count'
      )
      setUnreadCount(data.count)
    } catch (err) {
      console.error('Error loading unread count:', err)
    }
  }

  if (unreadCount === 0) return null

  return (
    <span className={`inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 text-xs font-bold text-white bg-red-500 rounded-full ${className}`}>
      {unreadCount > 99 ? '99+' : unreadCount}
    </span>
  )
}
