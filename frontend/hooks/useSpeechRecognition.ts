'use client'

import { useState, useEffect, useRef, useCallback } from 'react'

// Extend Window interface for Web Speech API
interface SpeechRecognitionEvent {
  resultIndex: number
  results: {
    [index: number]: {
      isFinal: boolean
      [index: number]: {
        transcript: string
        confidence?: number
      }
    }
    length: number
  }
}

interface SpeechRecognitionErrorEvent {
  error: string
}

interface SpeechRecognitionInstance {
  continuous: boolean
  interimResults: boolean
  lang: string
  onstart: (() => void) | null
  onend: (() => void) | null
  onresult: ((event: SpeechRecognitionEvent) => void) | null
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null
  start: () => void
  stop: () => void
  abort: () => void
}

interface SpeechRecognitionConstructor {
  new (): SpeechRecognitionInstance
}

declare global {
  interface Window {
    SpeechRecognition: SpeechRecognitionConstructor
    webkitSpeechRecognition: SpeechRecognitionConstructor
  }
}

interface SpeechRecognitionState {
  isListening: boolean
  isSupported: boolean
  error: string | null
  transcript: string
}

interface UseSpeechRecognitionOptions {
  onResult?: (transcript: string, isFinal: boolean, confidence?: number) => void
  onError?: (error: string) => void
  continuous?: boolean
  interimResults?: boolean
  lang?: string
}

export function useSpeechRecognition(options: UseSpeechRecognitionOptions = {}) {
  const {
    onResult,
    onError,
    continuous = true,
    interimResults = true,
    lang = 'en-US',
  } = options

  const [state, setState] = useState<SpeechRecognitionState>({
    isListening: false,
    isSupported: false,
    error: null,
    transcript: '',
  })

  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null)
  const isStartingRef = useRef<boolean>(false)
  const onResultRef = useRef(onResult)
  const onErrorRef = useRef(onError)

  // Update refs when callbacks change (without re-initializing recognition)
  useEffect(() => {
    onResultRef.current = onResult
    onErrorRef.current = onError
  }, [onResult, onError])

  useEffect(() => {
    // Check for browser support
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition

    if (!SpeechRecognition) {
      setState((prev) => ({
        ...prev,
        isSupported: false,
        error: 'Speech recognition is not supported in this browser',
      }))
      return
    }

    setState((prev) => ({ ...prev, isSupported: true }))

    // Initialize recognition
    const recognition = new SpeechRecognition()
    // Set continuous based on option, but default to false for better control
    recognition.continuous = continuous ?? false
    recognition.interimResults = interimResults
    recognition.lang = lang

    recognition.onstart = () => {
      isStartingRef.current = false
      setState((prev) => ({
        ...prev,
        isListening: true,
        error: null,
      }))
    }

    recognition.onend = () => {
      isStartingRef.current = false
      setState((prev) => ({
        ...prev,
        isListening: false,
      }))
    }

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let interimTranscript = ''
      let finalTranscript = ''
      let confidence: number | undefined

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i][0]
        const transcript = result.transcript
        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' '
          // Capture confidence from final result (0-1 scale)
          confidence = result.confidence
        } else {
          interimTranscript += transcript
          // Also capture confidence from interim if available
          if (result.confidence !== undefined) {
            confidence = result.confidence
          }
        }
      }

      const fullTranscript = finalTranscript || interimTranscript
      setState((prev) => ({
        ...prev,
        transcript: fullTranscript.trim(),
      }))

      // Use ref to get latest callback without re-initializing recognition
      // Only call onResult if there's actual speech content (not empty/whitespace)
      if (onResultRef.current) {
        const trimmedFinal = finalTranscript.trim()
        const trimmedInterim = interimTranscript.trim()

        if (trimmedFinal.length > 0) {
          onResultRef.current(trimmedFinal, true, confidence)
        } else if (trimmedInterim.length > 0) {
          onResultRef.current(trimmedInterim, false, confidence)
        }
        // Don't call onResult for empty transcripts - this prevents incorrect scoring from silence
      }
    }

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      console.error('Speech recognition error event:', event.error, event)
      isStartingRef.current = false

      let errorMessage = 'An error occurred with speech recognition'

      switch (event.error) {
        case 'no-speech':
          // Don't treat this as a fatal error - recognition will continue listening
          // Don't stop listening for this error, just log it
          console.log('No speech detected, continuing to listen...')
          return
        case 'audio-capture':
          errorMessage = 'No microphone found. Please check your microphone connection.'
          setState((prev) => ({
            ...prev,
            error: errorMessage,
            isListening: false,
          }))
          if (onErrorRef.current) {
            onErrorRef.current(errorMessage)
          }
          return
        case 'not-allowed':
          errorMessage = 'Microphone permission denied. Please allow microphone access in your browser settings.'
          setState((prev) => ({
            ...prev,
            error: errorMessage,
            isListening: false,
          }))
          if (onErrorRef.current) {
            onErrorRef.current(errorMessage)
          }
          return
        case 'network':
          errorMessage = 'Network error. Please check your internet connection.'
          setState((prev) => ({
            ...prev,
            error: errorMessage,
            isListening: false,
          }))
          if (onErrorRef.current) {
            onErrorRef.current(errorMessage)
          }
          return
        case 'aborted':
          // User stopped, not really an error - just reset state
          setState((prev) => ({
            ...prev,
            isListening: false,
          }))
          return
        case 'bad-grammar':
        case 'language-not-supported':
          errorMessage = `Speech recognition error: ${event.error}`
          setState((prev) => ({
            ...prev,
            error: errorMessage,
            isListening: false,
          }))
          if (onErrorRef.current) {
            onErrorRef.current(errorMessage)
          }
          return
        default:
          errorMessage = `Speech recognition error: ${event.error}`
      }

      // For other errors, stop listening and show error
      setState((prev) => ({
        ...prev,
        error: errorMessage,
        isListening: false,
      }))

      if (onErrorRef.current) {
        onErrorRef.current(errorMessage)
      }
    }

    recognitionRef.current = recognition

    console.log('Speech recognition initialized', {
      continuous,
      interimResults,
      lang,
      hasOnResult: !!onResult,
      hasOnError: !!onError
    })

    return () => {
      console.log('Cleaning up speech recognition')
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop()
        } catch {
          // Ignore errors during cleanup
        }
        recognitionRef.current = null
      }
      isStartingRef.current = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [continuous, interimResults, lang])

  const start = useCallback(() => {
    console.log('start() called', {
      hasRecognition: !!recognitionRef.current,
      isSupported: state.isSupported,
      isStarting: isStartingRef.current,
      isListening: state.isListening
    })

    if (!recognitionRef.current) {
      console.error('Recognition ref is null')
      setState((prev) => ({
        ...prev,
        error: 'Speech recognition not initialized',
      }))
      return
    }

    if (!state.isSupported) {
      console.error('Speech recognition not supported')
      setState((prev) => ({
        ...prev,
        error: 'Speech recognition is not supported in this browser',
      }))
      return
    }

    // Prevent multiple simultaneous start attempts
    if (isStartingRef.current) {
      console.log('Already starting, ignoring start request')
      return
    }

    if (state.isListening) {
      console.log('Already listening, ignoring start request')
      return
    }

    isStartingRef.current = true

    // Optimistically set listening state immediately for better UX
    setState((prev) => ({
      ...prev,
      isListening: true,
      error: null,
    }))

    try {
      console.log('Calling recognition.start()')
      recognitionRef.current.start()
    } catch (error: unknown) {
      const err = error instanceof Error ? error : null
      if (err?.name === 'InvalidStateError') {
        console.log('Recognition already started, ignoring')
        isStartingRef.current = false
        return
      }

      console.error('Error starting recognition:', error)
      setState((prev) => ({
        ...prev,
        isListening: false,
        error: err?.message || 'Failed to start speech recognition. Please check microphone permissions.',
      }))
      isStartingRef.current = false

      if (err?.name === 'NotAllowedError' || err?.message?.includes('permission')) {
        setState((prev) => ({
          ...prev,
          error: 'Microphone permission denied. Please allow microphone access in your browser settings.',
        }))
      }
    }
  }, [state.isSupported, state.isListening])

  const stop = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
  }, [])

  const abort = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.abort()
    }
  }, [])

  return {
    ...state,
    start,
    stop,
    abort,
  }
}
