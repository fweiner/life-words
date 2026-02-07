'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api/client'
import type { VoiceGender } from '@/lib/utils/textToSpeech'

/**
 * Hook to get and manage the user's voice preference
 * Returns the voice gender preference from the user's profile
 */
export function useVoicePreference(): VoiceGender {
  const [voiceGender, setVoiceGender] = useState<VoiceGender>('female')
  useEffect(() => {
    const loadPreference = async () => {
      try {
        const profile = await apiClient.get<{ voice_gender?: string }>('/api/profile')
        if (profile.voice_gender) {
          setVoiceGender(profile.voice_gender as VoiceGender)
        }
      } catch (err) {
        console.error('Error loading voice preference:', err)
      }
    }

    loadPreference()
  }, [])

  return voiceGender
}
