'use client'

import { useState, useRef, useCallback } from 'react'
import { apiClient } from '@/lib/api/client'

interface VoiceRecorderProps {
  onRecordingComplete: (url: string, duration: number) => void
  isPublic?: boolean
  maxDuration?: number // seconds
}

export function VoiceRecorder({
  onRecordingComplete,
  isPublic = false,
  maxDuration = 120 // 2 minutes default
}: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [duration, setDuration] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  const getMimeType = () => {
    const types = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/mp4',
      'audio/ogg;codecs=opus'
    ]
    return types.find(type => MediaRecorder.isTypeSupported(type)) || 'audio/webm'
  }

  const uploadVoice = useCallback(async (blob: Blob, recordedDuration: number) => {
    setIsUploading(true)
    setError(null)
    try {
      const formData = new FormData()
      const ext = blob.type.includes('mp4') ? 'mp4' : 'webm'
      formData.append('file', blob, `voice.${ext}`)

      const uploadPath = isPublic
        ? '/api/life-words/messaging/public/upload-media?media_type=voice'
        : '/api/life-words/messaging/upload-media?media_type=voice'

      const data = await apiClient.postFormData<{ url: string }>(
        uploadPath,
        formData,
        !isPublic
      )
      onRecordingComplete(data.url, recordedDuration)

    } catch (err) {
      console.error('Error uploading voice:', err)
      setError('Failed to upload voice message')
    } finally {
      setIsUploading(false)
      setDuration(0)
    }
  }, [isPublic, onRecordingComplete])

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)

      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
  }, [isRecording])

  const startRecording = useCallback(async () => {
    setError(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream

      const mimeType = getMimeType()
      const mediaRecorder = new MediaRecorder(stream, { mimeType })
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = async () => {
        // Stop all tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop())
        }

        // Create blob and upload
        const blob = new Blob(chunksRef.current, { type: mimeType })
        await uploadVoice(blob, duration)
      }

      mediaRecorder.start(1000) // Collect data every second
      setIsRecording(true)
      setDuration(0)

      // Start timer
      timerRef.current = setInterval(() => {
        setDuration(prev => {
          if (prev >= maxDuration - 1) {
            stopRecording()
            return prev
          }
          return prev + 1
        })
      }, 1000)

    } catch (err: any) {
      console.error('Error starting recording:', err)
      if (err.name === 'NotAllowedError') {
        setError('Microphone permission denied')
      } else {
        setError('Could not access microphone')
      }
    }
  }, [maxDuration, duration, uploadVoice, stopRecording])

  const cancelRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      // Remove the onstop handler to prevent upload
      mediaRecorderRef.current.onstop = null
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setDuration(0)

      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }

      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
    }
  }, [isRecording])

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 text-red-500 text-sm">
        <span>{error}</span>
        <button onClick={() => setError(null)} className="underline">
          Dismiss
        </button>
      </div>
    )
  }

  if (isUploading) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg">
        <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <span className="text-gray-600 text-sm">Uploading...</span>
      </div>
    )
  }

  if (isRecording) {
    return (
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-2 px-3 py-2 bg-red-50 rounded-lg">
          <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
          <span className="text-red-600 font-mono text-sm">{formatDuration(duration)}</span>
        </div>
        <button
          onClick={stopRecording}
          className="p-2 bg-green-500 text-white rounded-full hover:bg-green-600"
          title="Send"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
        <button
          onClick={cancelRecording}
          className="p-2 bg-gray-200 text-gray-600 rounded-full hover:bg-gray-300"
          title="Cancel"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </button>
      </div>
    )
  }

  return (
    <button
      onClick={startRecording}
      className="p-2 bg-gray-100 text-gray-600 rounded-full hover:bg-gray-200"
      title="Record voice message"
    >
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1 1.93c-3.94-.49-7-3.85-7-7.93h2c0 2.76 2.24 5 5 5s5-2.24 5-5h2c0 4.08-3.06 7.44-7 7.93V19h4v2H8v-2h4v-3.07z"/>
      </svg>
    </button>
  )
}
