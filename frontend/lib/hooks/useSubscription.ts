import { useState, useEffect, useCallback } from 'react'
import { apiClient } from '@/lib/api/client'
import type { SubscriptionStatus } from '@/lib/api/types'

export function useSubscription() {
  const [subscription, setSubscription] = useState<SubscriptionStatus | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchSubscription = useCallback(async () => {
    try {
      const data = await apiClient.get<SubscriptionStatus>('/api/stripe/status')
      setSubscription(data)
    } catch {
      setSubscription(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchSubscription()
  }, [fetchSubscription])

  return { subscription, loading, refresh: fetchSubscription }
}
