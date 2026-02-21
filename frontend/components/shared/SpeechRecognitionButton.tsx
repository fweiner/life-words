'use client'

import { useEffect, useRef, useCallback, useState } from 'react'
import { useSpeechRecognition } from '@/hooks/useSpeechRecognition'
import { extractAnswer } from '@/lib/api/matching'

interface SpeechRecognitionButtonProps {
  onResult: (transcript: string, confidence?: number) => void
  disabled?: boolean
  resetTrigger?: number // Increment this to force reset
  timer?: number // Timer value for better disabled message
  isCorrectAnswer?: boolean // Indicates if this is a correct answer (vs timer expired)
  onStartListening?: () => void | Promise<void> // Callback when user starts listening (can be async)
  autoStart?: boolean // Auto-start listening when component mounts
  onListeningChange?: (isListening: boolean) => void // Callback when listening state changes
  onNoResponse?: () => void // Callback when user doesn't respond after timeout
  noResponseTimeout?: number // Seconds to wait before calling onNoResponse (default 60)
}

export default function SpeechRecognitionButton({
  onResult,
  disabled = false,
  resetTrigger = 0,
  timer,
  isCorrectAnswer = false,
  onStartListening,
  autoStart = false,
  onListeningChange,
  onNoResponse,
  noResponseTimeout = 60,
}: SpeechRecognitionButtonProps) {
  const lastInterimRef = useRef<string>('')
  const lastConfidenceRef = useRef<number | undefined>(undefined)
  const hasSubmittedRef = useRef<boolean>(false)
  const hasEverListenedRef = useRef<boolean>(false) // Track if we've ever started listening
  const noResponseTimerRef = useRef<NodeJS.Timeout | null>(null) // Overall timeout for no response
  const [isInitializing, setIsInitializing] = useState(autoStart) // Track auto-start initialization

  // Function to submit an answer
  const submitAnswer = useCallback(async (transcript: string, confidence?: number) => {
    if (hasSubmittedRef.current) return

    // Don't submit empty or very short transcripts (likely noise or silence)
    const trimmed = transcript.trim()
    if (trimmed.length < 2) {
      console.log('Ignoring empty/short transcript:', JSON.stringify(trimmed))
      return
    }

    hasSubmittedRef.current = true
    try {
      const answer = await extractAnswer(transcript)
      onResult(answer, confidence)
    } catch {
      // Fallback to raw transcript if API fails
      onResult(transcript.trim(), confidence)
    }
  }, [onResult])

  const { isListening, isSupported, error, start, stop, transcript, abort } =
    useSpeechRecognition({
      continuous: true, // Keep listening until we manually stop
      onResult: (transcript, isFinal, confidence) => {
        // Store confidence for later use
        if (confidence !== undefined) {
          lastConfidenceRef.current = confidence
        }

        // Store interim results for display
        if (transcript.trim().length >= 2) {
          lastInterimRef.current = transcript
        }

        // Only submit on final results - no timeout auto-submit
        // This gives users unlimited time to speak
        if (isFinal && transcript.trim().length >= 2) {
          // Clear the no-response timeout on successful speech
          if (noResponseTimerRef.current) {
            clearTimeout(noResponseTimerRef.current)
            noResponseTimerRef.current = null
          }
          submitAnswer(transcript, confidence)
          stop()
        }
      },
      onError: (error) => {
        // Suppress 'no-speech' error - it's expected when user hasn't spoken yet
        if (error === 'no-speech' || error?.includes?.('no-speech')) {
          console.log('No speech detected - will auto-restart')
          return
        }
        console.error('Speech recognition error:', error)
      },
    })

  // Reset state when resetTrigger changes (new item)
  useEffect(() => {
    hasSubmittedRef.current = false
    hasEverListenedRef.current = false
    lastInterimRef.current = ''
    lastConfidenceRef.current = undefined
    // Clear any pending no-response timeout
    if (noResponseTimerRef.current) {
      clearTimeout(noResponseTimerRef.current)
      noResponseTimerRef.current = null
    }
    // Reset initializing state for autoStart
    if (autoStart) {
      setIsInitializing(true)
    }
  }, [resetTrigger, autoStart])

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (noResponseTimerRef.current) {
        clearTimeout(noResponseTimerRef.current)
      }
    }
  }, [])

  // Notify parent when listening state changes
  useEffect(() => {
    onListeningChange?.(isListening)
  }, [isListening, onListeningChange])

  // Auto-start listening when component mounts if autoStart is true
  useEffect(() => {
    if (autoStart && isSupported && !disabled) {
      console.log('Auto-starting speech recognition')
      setIsInitializing(true)
      // Small delay to ensure everything is ready
      const timer = setTimeout(async () => {
        // Wait for onStartListening to complete (e.g., TTS prompt) before starting recognition
        // This prevents speech recognition from picking up the TTS audio
        try {
          await onStartListening?.()
        } catch (e) {
          console.warn('onStartListening failed:', e)
        }
        // Add small delay after TTS to avoid echo pickup
        await new Promise(resolve => setTimeout(resolve, 300))
        hasEverListenedRef.current = true
        setIsInitializing(false)

        // Start the overall no-response timeout
        if (onNoResponse && noResponseTimeout > 0) {
          console.log(`Starting ${noResponseTimeout}s no-response timeout`)
          noResponseTimerRef.current = setTimeout(() => {
            if (!hasSubmittedRef.current) {
              console.log('No response timeout reached')
              hasSubmittedRef.current = true
              onNoResponse()
            }
          }, noResponseTimeout * 1000)
        }

        start()
      }, 500)
      return () => clearTimeout(timer)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoStart, isSupported])

  // Auto-restart listening if it stops without a result (for autoStart mode)
  // Restarts indefinitely until user speaks or timeout is reached
  useEffect(() => {
    if (autoStart && isSupported && !disabled && !isListening && !hasSubmittedRef.current && hasEverListenedRef.current) {
      console.log('Speech recognition stopped, restarting...')

      // Clear interim state before restarting
      lastInterimRef.current = ''
      lastConfidenceRef.current = undefined

      const timer = setTimeout(() => {
        if (!hasSubmittedRef.current && !disabled) {
          start()
        }
      }, 500)
      return () => clearTimeout(timer)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoStart, isSupported, isListening, disabled])

  // Reset when resetTrigger changes (e.g., new image, timeout)
  useEffect(() => {
    if (isListening) {
      console.log('Resetting speech recognition due to resetTrigger change')
      abort()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resetTrigger]) // Only depend on resetTrigger to avoid infinite loops

  const handleClick = async () => {
    console.log('Button clicked', { isListening, disabled })
    if (isListening) {
      console.log('Stopping recognition')
      stop()
    } else {
      console.log('Starting recognition')
      // Call onStartListening callback before starting (for first image prompt)
      // Wait for it to complete (e.g., TTS) before starting recognition
      try {
        await onStartListening?.()
      } catch (e) {
        console.warn('onStartListening failed:', e)
      }
      hasEverListenedRef.current = true
      start()
    }
  }

  if (!isSupported) {
    return (
      <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-6 text-center max-w-2xl">
        <p className="text-xl text-yellow-800 mb-2">Speech recognition is not supported in this browser.</p>
        <p className="text-lg text-yellow-700">Please use Chrome or Edge for the best experience.</p>
      </div>
    )
  }

  return (
    <div className="text-center w-full max-w-2xl">
      {disabled && !isListening && (
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4 mb-4" role="alert">
          <p className="text-xl text-blue-800">
            {timer !== undefined && timer === 0
              ? (isCorrectAnswer
                  ? 'Correct! Wait for the next image.'
                  : 'Time expired. Please wait for the next image.')
              : 'Processing answer...'}
          </p>
        </div>
      )}

      {isListening ? (
        <div className="w-full py-8 px-12 rounded-lg text-2xl font-bold bg-green-100 border-4 border-green-500 mb-4" style={{ minHeight: '80px' }}>
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="animate-pulse">
              <svg className="w-10 h-10 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <circle cx="4" cy="10" r="2" />
                <circle cx="10" cy="10" r="2" />
                <circle cx="16" cy="10" r="2" />
              </svg>
            </div>
            <span className="text-green-800">🎤 Listening...</span>
          </div>
          <p className="text-xl text-green-700 font-normal">Say the object&apos;s name now</p>
          <button
            type="button"
            className="mt-4 bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-6 rounded-lg text-lg transition-colors"
            onClick={handleClick}
          >
            Stop Listening
          </button>
        </div>
      ) : isInitializing ? (
        // Don't show anything while initializing - just wait for listening state
        null
      ) : (
        <button
          type="button"
          className="w-full py-8 px-12 rounded-lg text-2xl font-bold transition-colors focus:outline-none focus:ring-4 focus:ring-offset-2 bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white focus:ring-[var(--color-primary)]"
          onClick={handleClick}
          disabled={disabled}
          style={{ minHeight: '80px' }}
          aria-label="Click and say the object's name"
        >
          <div className="flex items-center justify-center gap-3">
            <span className="text-3xl">🎤</span>
            <span>Click to start (or restart) listening</span>
          </div>
        </button>
      )}

      {transcript && (
        <div className="mt-6 bg-gray-50 border-2 border-gray-200 rounded-lg p-4">
          <p className="text-gray-600 text-lg mb-2">You said:</p>
          <p className="text-2xl font-bold text-gray-900">{transcript}</p>
        </div>
      )}

      {error && (
        <div className="mt-6 bg-red-50 border-2 border-red-300 rounded-lg p-4" role="alert">
          <p className="text-red-700 text-xl font-semibold">{error}</p>
        </div>
      )}
    </div>
  )
}
